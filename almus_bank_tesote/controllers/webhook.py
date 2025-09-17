# -*- coding: utf-8 -*-
import json
import logging
from odoo import http, _
from odoo.http import request
from werkzeug.exceptions import Forbidden, BadRequest

_logger = logging.getLogger(__name__)

class TesoteWebhookController(http.Controller):
    """
    Controller for handling Tesote webhook notifications
    Compatible with Odoo 17 and 18
    """
    
    @http.route('/tesote/webhook/<int:webhook_id>', 
                type='json', auth='public', methods=['POST'], csrf=False)
    def tesote_webhook(self, webhook_id, **kwargs):
        """
        Receive and process Tesote webhook events
        
        Expected headers:
        - X-Tesote-Signature: HMAC signature of the payload
        - X-Tesote-Event: Event type (transaction.created, account.updated, etc.)
        """
        try:
            # Check if webhooks are enabled
            IrConfigParam = request.env['ir.config_parameter'].sudo()
            if not IrConfigParam.get_param('tesote.webhook_enabled'):
                _logger.warning("Tesote webhook called but webhooks are disabled")
                return {'status': 'disabled'}
            
            # Get webhook configuration
            webhook = request.env['tesote.webhook'].sudo().browse(webhook_id)
            if not webhook.exists() or not webhook.active:
                _logger.warning(f"Invalid or inactive webhook ID: {webhook_id}")
                raise Forbidden("Invalid webhook")
            
            # Get request data
            payload = request.jsonrequest
            headers = request.httprequest.headers
            
            # Verify signature
            signature = headers.get('X-Tesote-Signature')
            if not signature:
                _logger.warning("Missing signature in Tesote webhook")
                raise BadRequest("Missing signature")
            
            # Verify the payload signature
            payload_str = json.dumps(payload, separators=(',', ':'), ensure_ascii=False)
            if not webhook.verify_signature(payload_str, signature):
                _logger.error("Invalid signature in Tesote webhook")
                raise Forbidden("Invalid signature")
            
            # Get event type
            event_type = headers.get('X-Tesote-Event', payload.get('event'))
            if not event_type:
                _logger.warning("Missing event type in Tesote webhook")
                raise BadRequest("Missing event type")
            
            # Process the event
            _logger.info(f"Processing Tesote webhook event: {event_type}")
            webhook.process_webhook_event(event_type, payload)
            
            # Return success response
            return {
                'status': 'success',
                'message': f'Event {event_type} processed successfully'
            }
            
        except (Forbidden, BadRequest) as e:
            # These are expected errors, return appropriate status
            raise e
            
        except Exception as e:
            # Unexpected error, log it but don't expose details
            _logger.exception(f"Error processing Tesote webhook: {str(e)}")
            return {
                'status': 'error',
                'message': 'Internal error processing webhook'
            }
    
    @http.route('/tesote/webhook/test', 
                type='http', auth='user', methods=['GET'])
    def test_webhook_endpoint(self, **kwargs):
        """
        Test endpoint to verify webhook URL is accessible
        Only accessible to authenticated users
        """
        user = request.env.user
        if not user.has_group('account.group_account_manager'):
            raise Forbidden("Access denied")
        
        return request.make_response(
            json.dumps({
                'status': 'ok',
                'message': 'Tesote webhook endpoint is working',
                'version': '17.0',  # Odoo version
                'user': user.name
            }),
            headers=[('Content-Type', 'application/json')]
        )
