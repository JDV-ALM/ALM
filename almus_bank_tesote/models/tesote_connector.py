# -*- coding: utf-8 -*-
# Almus Dev (JDV-ALM) - www.almus.dev
# Conector Tesote con protección contra bucles y timeouts

import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time

_logger = logging.getLogger(__name__)


class TesoteConnector:
    """
    Conector seguro para Tesote API v2.0.0
    Con protecciones anti-bucle y timeouts cortos
    """
    
    # Constantes de seguridad
    MAX_RETRIES = 2  # Máximo 2 reintentos
    TIMEOUT_SECONDS = 10  # Timeout corto de 10 segundos
    MAX_TRANSACTIONS_PER_SYNC = 100  # Límite de transacciones por sincronización
    MIN_REQUEST_INTERVAL = 1.0  # 1 segundo mínimo entre requests
    
    def __init__(self, token: str, base_url: str = 'https://equipo.tesote.com/api/v2'):
        """
        Inicializar conector con medidas de seguridad
        
        :param token: Bearer token para autenticación
        :param base_url: URL base de la API
        """
        self.token = token
        self.base_url = base_url.rstrip('/')
        
        # Sesión HTTP con configuración segura
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Client': 'Odoo-Almus-Tesote/1.0',
        })
        
        # Control de rate limiting y anti-bucle
        self.last_request_time = None
        self.request_count = 0
        self.max_requests_per_session = 20  # Límite de requests por sesión
        
    def _check_rate_limit(self):
        """Verificar y aplicar límites de tasa"""
        # Verificar límite de requests por sesión
        if self.request_count >= self.max_requests_per_session:
            raise Exception(f"Límite de {self.max_requests_per_session} requests alcanzado. Previniendo bucle.")
        
        # Aplicar intervalo mínimo entre requests
        if self.last_request_time:
            elapsed = (datetime.now() - self.last_request_time).total_seconds()
            if elapsed < self.MIN_REQUEST_INTERVAL:
                time.sleep(self.MIN_REQUEST_INTERVAL - elapsed)
    
    def _make_request(self, method: str, endpoint: str, retry_count: int = 0, **kwargs) -> Optional[Dict]:
        """
        Realizar petición HTTP con protecciones anti-bucle
        
        :param method: Método HTTP (GET, POST, etc)
        :param endpoint: Endpoint de la API
        :param retry_count: Contador interno de reintentos
        :return: Respuesta JSON o None si hay error
        """
        # Protección contra bucles de reintentos
        if retry_count > self.MAX_RETRIES:
            _logger.error(f"Máximo de reintentos alcanzado para {endpoint}")
            return None
        
        # Aplicar rate limiting
        try:
            self._check_rate_limit()
        except Exception as e:
            _logger.error(str(e))
            return None
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            # Request con timeout corto
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.TIMEOUT_SECONDS,
                **kwargs
            )
            
            # Actualizar contadores
            self.last_request_time = datetime.now()
            self.request_count += 1
            
            # Manejar respuestas de error
            if response.status_code == 429:  # Rate limit de la API
                _logger.warning(f"Rate limit alcanzado en Tesote API")
                # NO reintentar para evitar bucles
                return None
            
            if response.status_code == 401:  # Token inválido
                _logger.error("Token de Tesote inválido o expirado")
                return None
            
            if response.status_code >= 500:  # Error del servidor
                _logger.warning(f"Error del servidor Tesote: {response.status_code}")
                # Un solo reintento para errores de servidor
                if retry_count == 0:
                    time.sleep(2)  # Esperar 2 segundos
                    return self._make_request(method, endpoint, retry_count + 1, **kwargs)
                return None
            
            if response.status_code >= 400:
                _logger.error(f"Error en Tesote API: {response.status_code} - {response.text[:100]}")
                return None
            
            return response.json() if response.text else {}
            
        except requests.exceptions.Timeout:
            _logger.error(f"Timeout ({self.TIMEOUT_SECONDS}s) en petición a: {endpoint}")
            return None
        except requests.exceptions.ConnectionError:
            _logger.error(f"Error de conexión con Tesote: {endpoint}")
            return None
        except Exception as e:
            _logger.error(f"Error inesperado en Tesote API: {str(e)[:100]}")
            return None
    
    def test_connection(self) -> bool:
        """
        Verificar conexión con la API (con timeout corto)
        
        :return: True si la conexión es exitosa
        """
        # Reset contador para prueba de conexión
        self.request_count = 0
        
        try:
            # Hacer request simple con timeout extra corto
            response = self.session.get(
                f"{self.base_url}/accounts",
                timeout=5,
                params={'limit': 1}  # Solo verificar, no cargar todo
            )
            return response.status_code == 200
        except:
            return False
    
    def get_accounts(self, limit: int = 50) -> List[Dict]:
        """
        Obtener lista de cuentas bancarias con límite
        
        :param limit: Número máximo de cuentas a obtener
        :return: Lista de cuentas o lista vacía si hay error
        """
        # Reset contador por sesión
        self.request_count = 0
        
        params = {
            'limit': min(limit, 50),  # Máximo 50 cuentas
            'status': 'active'  # Solo cuentas activas
        }
        
        response = self._make_request('GET', '/accounts', params=params)
        
        if not response:
            return []
        
        # Extraer cuentas de la respuesta
        if isinstance(response, dict) and 'data' in response:
            accounts = response.get('data', [])
        elif isinstance(response, list):
            accounts = response[:limit]  # Aplicar límite
        else:
            return []
        
        # Procesar y validar cuentas
        valid_accounts = []
        for acc in accounts[:limit]:  # Doble seguridad en límite
            if isinstance(acc, dict) and acc.get('id'):
                valid_accounts.append({
                    'id': acc.get('id'),
                    'bank_name': acc.get('bank_name', 'Unknown')[:50],  # Limitar longitud
                    'masked_account': acc.get('masked_account', 'XXXX')[:20],
                    'currency': acc.get('currency', 'VES')[:3],
                    'legal_entity_name': acc.get('legal_entity_name', '')[:100],
                    'balance': float(acc.get('balance', 0.0)),
                })
        
        _logger.info(f"Obtenidas {len(valid_accounts)} cuentas de Tesote")
        return valid_accounts
    
    def get_transactions(self, account_id: str, date_from: datetime = None, 
                        date_to: datetime = None) -> List[Dict]:
        """
        Obtener transacciones con límites estrictos
        
        :param account_id: ID de la cuenta en Tesote
        :param date_from: Fecha inicial (máximo 30 días atrás)
        :param date_to: Fecha final
        :return: Lista de transacciones limitada
        """
        # Validar y limitar rango de fechas
        if not date_to:
            date_to = datetime.now()
        if not date_from:
            date_from = date_to - timedelta(days=7)  # Por defecto solo 7 días
        
        # Limitar a máximo 30 días para evitar cargas excesivas
        max_days = 30
        delta = (date_to - date_from).days
        if delta > max_days:
            date_from = date_to - timedelta(days=max_days)
            _logger.warning(f"Rango de fechas limitado a {max_days} días")
        
        # Parámetros con límites estrictos
        params = {
            'start_date': date_from.strftime('%Y-%m-%d'),
            'end_date': date_to.strftime('%Y-%m-%d'),
            'limit': self.MAX_TRANSACTIONS_PER_SYNC,  # Límite fijo
        }
        
        response = self._make_request(
            'GET', 
            f'/accounts/{account_id}/transactions',
            params=params
        )
        
        if not response:
            return []
        
        # Extraer transacciones
        if isinstance(response, dict) and 'data' in response:
            transactions = response.get('data', [])
        elif isinstance(response, list):
            transactions = response
        else:
            return []
        
        # Limitar y procesar transacciones
        valid_transactions = []
        for txn in transactions[:self.MAX_TRANSACTIONS_PER_SYNC]:
            if not isinstance(txn, dict) or not txn.get('id'):
                continue
            
            # Solo campos esenciales para reducir memoria
            valid_transactions.append({
                'id': str(txn.get('id'))[:50],
                'date': str(txn.get('date', ''))[:10],
                'amount': float(txn.get('amount', 0.0)),
                'description': str(txn.get('description', ''))[:200],
                'reference': str(txn.get('reference', txn.get('id', '')))[:50],
                'type': str(txn.get('type', 'other'))[:10],
            })
        
        _logger.info(f"Obtenidas {len(valid_transactions)} transacciones para cuenta {account_id}")
        return valid_transactions
    
    def get_account_balance(self, account_id: str) -> Optional[float]:
        """
        Obtener balance con request único
        
        :param account_id: ID de la cuenta
        :return: Balance o None
        """
        response = self._make_request('GET', f'/accounts/{account_id}', params={'fields': 'balance'})
        
        if response and isinstance(response, dict):
            return float(response.get('balance', 0.0))
        
        return None
    
    def process_webhook(self, payload: Dict) -> Dict:
        """
        Procesar payload de webhook (llamado desde automatización)
        
        :param payload: Datos del webhook
        :return: Diccionario con resultado del procesamiento
        """
        event_type = payload.get('event')
        data = payload.get('data', {})
        
        result = {
            'success': False,
            'message': '',
            'action': None
        }
        
        if event_type == 'transaction.created':
            # Nueva transacción - preparar para sincronización
            account_id = data.get('account_id')
            if account_id:
                result['action'] = 'sync_account'
                result['account_id'] = account_id
                result['success'] = True
                result['message'] = f"Nueva transacción detectada para cuenta {account_id}"
        
        elif event_type == 'account.updated':
            # Cuenta actualizada
            account_id = data.get('id')
            if account_id:
                result['action'] = 'update_account'
                result['account_id'] = account_id
                result['success'] = True
                result['message'] = f"Actualización detectada para cuenta {account_id}"
        
        return result