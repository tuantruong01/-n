from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class IrSequenceInherit(models.Model):
    _inherit = 'ir.sequence'

    @api.model
    def next_by_code(self, sequence_code, sequence_date=None):
        """ Draw an interpolated string using a sequence with the requested code.
            If several sequences with the correct code are available to the user
            (multi-company cases), the one from the user's current company will
            be used.
        """
        self.check_access_rights('read')
        seq_ids = self.search([('code', '=', sequence_code)], order='company_id')
        if not seq_ids:
            _logger.debug(
                "No ir.sequence has been found for code '%s'. Please make sure a sequence is set for current company." % sequence_code)
            return False
        seq_id = seq_ids[0]
        return seq_id._next(sequence_date=sequence_date)
