# -*- coding: utf-8 -*-
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time

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
        if self.env and 'tesote.api.log' in self.env:
            self.env['tesote.api.log'].sudo().create({
                'endpoint': endpoint,
                'method': method,
                'status_code': status_code,
                'response_time': response_time,
                'error_message': error_message,
                'account_id': account_id.id if account_id else False,
            })
    
    def _handle_rate_limit(self, response):
        """Handle API rate limiting"""
        if 'X-RateLimit-Remaining' in response.headers:
            self._rate_limit_remaining = int(response.headers['X-RateLimit-Remaining'])
        if 'X-RateLimit-Reset' in response.headers:
            self._rate_limit_reset = int(response.headers['X-RateLimit-Reset'])
        
        if response.status_code == 429:  # Too Many Requests
            retry_after = response.headers.get('Retry-After', 60)
            _logger.warning(f"Rate limit exceeded. Retrying after {retry_after} seconds")
            time.sleep(int(retry_after))
            return True
        return False
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test API connection and token validity"""
        try:
            start_time = time.time()
            response = self.session.get(f'{self.base_url}/accounts', params={'per_page': 1})
            response_time = int((time.time() - start_time) * 1000)
            
            self._log_api_call('/accounts', 'GET', response.status_code, response_time)
            
            if response.status_code == 200:
                return True, "Connection successful"
            elif response.status_code == 401:
                return False, "Invalid API token"
            else:
                return False, f"Connection failed: HTTP {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            _logger.error(f"Tesote API connection error: {str(e)}")
            return False, f"Connection error: {str(e)}"
    
    def get_accounts(self) -> List[Dict]:
        """
        Fetch all bank accounts from Tesote with pagination
        Returns list of account dictionaries
        """
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
                    
                    if self._handle_rate_limit(response):
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
                    
            else:  # All retries exhausted
                break
                
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
            
            if self._handle_rate_limit(response):
                # Retry once after rate limit
                response = self.session.get(
                    f'{self.base_url}/accounts/{account_id}/transactions',
                    params=params,
                    timeout=30
                )
            
            self._log_api_call(f'/accounts/{account_id}/transactions', 'GET', 
                              response.status_code, response_time)
            
            if response.status_code != 200:
                error_msg = f"Failed to fetch transactions: HTTP {response.status_code}"
                raise TesoteAPIError(error_msg)
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            _logger.error(f"Error fetching transactions: {str(e)}")
            raise TesoteAPIError(f"Request failed: {str(e)}")
