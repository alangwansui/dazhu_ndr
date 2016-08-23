# -*- encoding: utf-8 -*-
##############################################################################
#
#    Daniel Campos (danielcampos@avanzosc.es) Date: 08/09/2014
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################
import urllib2
import urllib
from openerp.osv import fields, osv
from openerp import SUPERUSER_ID
from openerp.exceptions import Warning
from openerp import tools


class project_project(osv.osv):
    _inherit = 'project.project'

    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image)
        return result

    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image(value, size=(550, 350), )}, context=context)

    def _task_count_available(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for project in self.browse(cr, uid, ids, dict(context, active_test=False)):
            count = sum([x.stage_id.name.lower() == 'available' and 1 or 0 for x in project.task_ids])
            res[project.id] = count
        return res

    def _task_count_reserved(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for project in self.browse(cr, uid, ids, dict(context, active_test=False)):
            count = sum([x.stage_id.name.lower() == 'reserved' and 1 or 0 for x in project.task_ids])
            res[project.id] = count
        return res

    _columns = {
        'url': fields.char('Out web URL', size=300),
        'image': fields.binary("Photo",
                               help="This field holds the image used as photo for the employee, limited to 1024x1024px."),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
                                        string="Medium-sized photo", type="binary", multi="_get_image",
                                        store={
                                            'project.project': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
                                        },
                                        help="600X450"),
        'x_address_state': fields.char('State', size=32),
        'x_projectaddress': fields.char('Address', size=32),
        'x_projectbuilder': fields.char('Builder', size=32),
        'x_projectcommissionrate': fields.char('Commission Rate', size=32),
        'x_projectdeveloper': fields.char('Developer', size=32),
        'x_projectestcompletion': fields.char('Est.Completion', size=32),
        'x_projectfirb': fields.char('FIRB', size=32),
        'x_projectpricerange': fields.char('Price Range', size=32),
        'x_projectreservationfee': fields.char('Reservation Fee', size=32),
        'x_projectsuburb': fields.char('Suburb', size=32),
        'x_type': fields.selection([('off', 'Off the plan'), ('new', 'Brand New'), ('resale', 'Resale')], 'Type'),
        'x_state': fields.selection([('selling', 'Selling'), ('eoi', 'EOI'), ('sold', 'Sold')], 'Status'),

        'task_count_available': fields.function(_task_count_available, type='integer', string='Available'),
        'task_count_reserved': fields.function(_task_count_reserved, type='integer', sgring='Reserved'),

        'property_type': fields.char('Property Type', size=32),
        'completion_date': fields.char('Completion Date',size=50),
    }

    def open_task_stage(self, cr, uid, ids, context=None):
        task_obj = self.pool.get('project.task')
        domain = [('project_id', '=', ids[0])]

        stage_name = context.get('stage_name', '')

        domain = [('project_id', '=', ids[0])]
        if stage_name:
            domain += [('stage_id.name', 'ilike', stage_name)]

        print domain

        return {
            'name': '%s Units' % stage_name,
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'view_mode': 'tree,form',
            'domain': domain,
        }

    def open_url(self, cr, uid, ids, context=None):
        me = self.browse(cr, uid, ids[0], context=None)
        url = me.url or ''
        if 'http' not in url:
            url = 'http://' + url

        return {
            'name': 'Floor Plan',
            'res_model': 'ir.actions.act_url',
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': url,
        }

    def post_json_data_to_php(self, cr, uid, ids, context=None):
        url = 'http://bjdemo.itpanda.com.au/odoo/test.php'
        if not ids:
            ids = self.search(cr, uid, [], context=context)

        data = {}
        req = urllib2.Request(url)
        data = urllib.urlencode(data)
        response = urllib2.urlopen(req, data)
        return response.read()


class project_task(osv.osv):
    _inherit = 'project.task'
    _inherits = {'project.project': 'project_id'}

    _columns = {
        'image_medium': fields.related('project_id', 'image_medium', type="binary", string="Image", readonly=True),
        'project_url': fields.related('project_id', 'url', type="char", string="URL", readonly=True),

        'url': fields.char(size=300),

        'x_aspect': fields.char('Aspec', size=32),
        'x_bathrooms': fields.char('Bathrooms', size=32),
        'x_bedrooms': fields.char('Bedrooms', size=32),
        'x_carspace': fields.char('Car Space', size=32),
        'x_storage2': fields.selection([('y', 'Y'), ('n', 'N')], 'Storage', size=32),

        'x_unitno': fields.char('Unit No.', size=32),
        'x_lotno': fields.char('Lot No.', size=32),
        'x_level': fields.char('Level', size=32),

        'x_int_area': fields.char('Int Area', size=32),
        'x_ext_aera': fields.char('Ext Area', size=32),
        'x_land_area': fields.char('Land Area', size=32),

        'x_houseprice': fields.float('House Price', size=32),
        'x_landprice': fields.float('Land Price', size=32),
        'x_totalprice': fields.float('Total Price', size=32),

        'x_currency_id': fields.many2one("res.currency", string="Currency"),
    }

    def default_get(self, cr, uid, fields, context=None):
        res = super(project_task, self).default_get(cr, uid, fields, context=context)
        currency_id = self.pool['res.users'].browse(cr, uid, uid, ).company_id.currency_id.id
        res.update({'x_currency_id': currency_id})
        return res

    def set_stage_reserved(self, cr, uid, ids, context=None):
        stage_obj = self.pool.get('project.task.type')
        stage_ids = stage_obj.search(cr, uid, [('name', '=', 'Reserved')], limit=1, context=context)
        if not stage_ids:
            raise Warning('Not found stage: Reserved')

        self.write(cr, uid, ids, {'stage_id': stage_ids[0]}, context=context)
        return True

    def open_url(self, cr, uid, ids, context=None):
        me = self.browse(cr, uid, ids[0], context=None)
        url = me.url or ''
        if 'http' not in url:
            url = 'http://' + url

        return {
            'name': 'Floor Plan',
            'res_model': 'ir.actions.act_url',
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': url,
        }




        ############################################################################
