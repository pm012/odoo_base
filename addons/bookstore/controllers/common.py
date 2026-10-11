import json
import logging

from odoo.http import request

_logger = logging.getLogger(__name__)


class ApiMixin:
    """
    Common helpers for REST API controllers.

    Used as a mixin together with http.Controller:
        class MyApi(http.Controller, ApiMixin):
            ...
    """

    # =========================================================
    # Response helpers
    # =========================================================

    def _success(self, data, status=200):
        """Successful JSON response with specified HTTP status."""
        return request.make_response(
            json.dumps(data, ensure_ascii=False, default=str),
            headers=[('Content-Type', 'application/json; charset=utf-8')],
            status=status,
        )

    def _error(self, message, status=400, extra=None):
        """
        Error JSON response.

        :param message: error message text
        :param status: HTTP status (400, 404, 500, ...)
        :param extra: dict — additional fields (e.g., {'field': 'name'})
        """
        body = {'error': message, 'status': status}
        if extra:
            body.update(extra)
        _logger.warning("API error [%s]: %s (extra=%s)", status, message, extra)
        return request.make_response(
            json.dumps(body, ensure_ascii=False),
            headers=[('Content-Type', 'application/json; charset=utf-8')],
            status=status,
        )

    # =========================================================
    # Request helpers
    # =========================================================

    def _parse_json_body(self):
        """
        Parses JSON request body.

        Returns a tuple (payload, error_response):
        - on success: (dict, None)
        - on error: (None, Response)

        Usage example:
            payload, error = self._parse_json_body()
            if error:
                return error
        """
        raw = request.httprequest.data
        if not raw:
            return None, self._error('Request body is empty', status=400)
        try:
            payload = json.loads(raw)
        except (ValueError, TypeError) as e:
            return None, self._error(f'Invalid JSON: {e}', status=400)
        if not isinstance(payload, dict):
            return None, self._error('JSON body must be an object', status=400)
        return payload, None

    # =========================================================
    # Validation helpers
    # =========================================================

    def _parse_int(self, value, field_name, default=None):
        """
        Parses an int from a query parameter.

        Returns a tuple (value, error_response):
        - on success: (int|None, None)
        - on error: (None, Response)

        Example:
            limit, error = self._parse_int(limit, 'limit')
            if error:
                return error
        """
        if value is None or value == '':
            return default, None
        try:
            return int(value), None
        except (ValueError, TypeError):
            return None, self._error(f'Parameter "{field_name}" must be an integer', status=400)

    # =========================================================
    # Domain helpers
    # =========================================================

    def _safe_domain(self, model, domain):
        """
        Verifies that all fields in the domain actually exist in the model.
        Prevents SQL injections via domain.
        """
        if not domain:
            return []
        valid_fields = set(model._fields.keys())
        cleaned = []
        for leaf in domain:
            if not isinstance(leaf, (list, tuple)) or len(leaf) != 3:
                continue
            field_name, operator, value = leaf
            if field_name not in valid_fields:
                _logger.warning("API: unknown field in domain: %s", field_name)
                continue
            cleaned.append((field_name, operator, value))
        return cleaned
