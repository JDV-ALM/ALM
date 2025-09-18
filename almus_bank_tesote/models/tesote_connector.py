# -*- coding: utf-8 -*-
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time
import json

_logger = logging.getLogger(__name__)

class TesoteAPIError(Exception):
    """Custom exception for Tesote API errors"""
    pass

class TesoteConnector:
    """
    Connector for Tesote API v2.0.0
    Handles authentication, pagination, and rate limiting
    """
    
    def __init__(self, token: str, base_url: str = None, env=None):
        self.token = token
        self.base_url = base_url or 'https://equipo.tesote.com/api/v2'
        self.env = env
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        })
        self._rate_limit_remaining = 100
        self._rate_limit_reset = None
    
    def _log_api_call(self, endpoint: str, method: str, status_code: int, 
                      response_time: int, error_message: str = None, account_id=None):
        """Log API calls for debugging and monitoring"""
        _logger.info(f"Tesote API Call: {method} {endpoint} - Status: {status_code} - Time: {response_time}ms")
        
        if self.env and 'tesote.api.log' in self.env:
            try:
                self.env['tesote.api.log'].sudo().create({
                    'endpoint': endpoint,
                    'method': method,
                    'status_code': status_code,
                    'response_time': response_time,
                    'error_message': error_message,
                    'account_id': account_id.id if account_id else False,
                })
            except Exception as e:
                _logger.error(f"Failed to log API call: {str(e)}")
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test API connection and token validity with timeout"""
        _logger.info(f"Testing Tesote connection to: {self.base_url}")
        
        try:
            start_time = time.time()
            
            # Usar timeout más corto para test de conexión
            response = self.session.get(
                f'{self.base_url}/accounts', 
                params={'per_page': 1},
                timeout=10  # 10 segundos timeout
            )
            
            response_time = int((time.time() - start_time) * 1000)
            
            self._log_api_call('/accounts', 'GET', response.status_code, response_time)
            
            if response.status_code == 200:
                _logger.info("Tesote connection successful")
                return True, "Connection successful"
            elif response.status_code == 401:
                _logger.error("Tesote API token is invalid")
                return False, "Invalid API token - Please check your token"
            elif response.status_code == 404:
                _logger.error(f"Tesote API URL not found: {self.base_url}")
                return False, f"API URL not found - Please check the URL: {self.base_url}"
            else:
                _logger.error(f"Tesote connection failed with status: {response.status_code}")
                return False, f"Connection failed: HTTP {response.status_code}"
                
        except requests.exceptions.Timeout:
            _logger.error("Tesote API connection timeout")
            return False, "Connection timeout - The API is not responding. Please check your internet connection and API URL"
            
        except requests.exceptions.ConnectionError as e:
            _logger.error(f"Tesote API connection error: {str(e)}")
            return False, f"Connection error - Cannot reach the API server. Please check the URL and your internet connection"
            
        except requests.exceptions.RequestException as e:
            _logger.error(f"Tesote API request error: {str(e)}")
            return False, f"Request error: {str(e)}"
            
        except Exception as e:
            _logger.error(f"Unexpected error testing Tesote connection: {str(e)}")
            return False, f"Unexpected error: {str(e)}"
    
    def get_accounts(self) -> List[Dict]:
        """
        Fetch all bank accounts from Tesote with pagination
        Returns list of account dictionaries
        """
        _logger.info("Fetching accounts from Tesote API")
        accounts = []
        page = 1
        max_retries = 3
        
        while True:
            retry_count = 0
            while retry_count < max_retries:
                try:
                    start_time = time.time()
                    response = self.session.get(
                        f'{self.base_url}/accounts',
                        params={'page': page, 'per_page': 50},
                        timeout=30
                    )
                    response_time = int((time.time() - start_time) * 1000)
                    
                    if response.status_code == 429:  # Rate limit
                        retry_after = response.headers.get('Retry-After', 60)
                        _logger.warning(f"Rate limit hit, waiting {retry_after} seconds")
                        time.sleep(int(retry_after))
                        retry_count += 1
                        continue
                    
                    self._log_api_call('/accounts', 'GET', response.status_code, response_time)
                    
                    if response.status_code != 200:
                        raise TesoteAPIError(f"Failed to fetch accounts: HTTP {response.status_code}")
                    
                    data = response.json()
                    accounts.extend(data.get('accounts', []))
                    
                    # Check pagination
                    pagination = data.get('pagination', {})
                    if page >= pagination.get('total_pages', 1):
                        break
                    page += 1
                    break
                    
                except requests.exceptions.Timeout:
                    retry_count += 1
                    if retry_count >= max_retries:
                        raise TesoteAPIError("Request timeout after multiple retries")
                    time.sleep(2 ** retry_count)  # Exponential backoff
                    
                except requests.exceptions.RequestException as e:
                    _logger.error(f"Error fetching accounts: {str(e)}")
                    raise TesoteAPIError(f"Request failed: {str(e)}")
                    
            else:  # All retries exhausted
                break
        
        _logger.info(f"Successfully fetched {len(accounts)} accounts")
        return accounts
    
    def get_transactions(self, account_id: str, start_date: str = None, 
                         end_date: str = None, after_id: str = None) -> Dict:
        """
        Fetch transactions for a specific account
        Uses cursor-based pagination with after_id
        """
        params = {'per_page': 100}
        
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        if after_id:
            params['transactions_after_id'] = after_id
        
        try:
            start_time = time.time()
            response = self.session.get(
                f'{self.base_url}/accounts/{account_id}/transactions',
                params=params,
                timeout=30
            )
            response_time = int((time.time() - start_time) * 1000)
            
            if response.status_code == 429:  # Rate limit
                retry_after = response.headers.get('Retry-After', 60)
                _logger.warning(f"Rate limit hit, waiting {retry_after} seconds")
                time.sleep(int(retry_after))
                
                # Retry once
                response = self.session.get(
                    f'{self.base_url}/accounts/{account_id}/transactions',
                    params=params,
                    timeout=30
                )
            
            self._log_api_call(f'/accounts/{account_id}/transactions', 'GET', 
                              response.status_code, response_time)
            
            if response.status_code != 200:
                error_msg = f"Failed to fetch transactions: HTTP {response.status_code}"
                if response.text:
                    try:
                        error_data = response.json()
                        error_msg += f" - {error_data.get('message', response.text)}"
                    except:
                        error_msg += f" - {response.text[:200]}"
                raise TesoteAPIError(error_msg)
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            _logger.error(f"Error fetching transactions: {str(e)}")
            raise TesoteAPIError(f"Request failed: {str(e)}")