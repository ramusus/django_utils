# -*- coding: utf-8 -*-
from django import template
from jspacker import JavaScriptPacker
from django.conf import settings

register = template.Library()

class PackedJSNode(template.Node):
    def __init__(self, nodelist, ready=False):
        self.nodelist = nodelist
        self.ready = ready

    def get_tags_around(self, code):
        ready_code = '''
            $(function() {
                %s
            })
            ''' % code
        return '''
            <script type="text/javascript">
            /*<![CDATA[*/
            %s
            /*]]>*/
            </script>
            ''' % (self.ready and ready_code or code)

    def render(self, context):
        p = JavaScriptPacker()
        script = self.nodelist.render(context).strip()
        #ugly test on empty script, no reason to pack such small scripts
        if 1 or settings.DEBUG == False or len(script) < 20:
            return self.get_tags_around(script)
        packed = p.pack(script, compaction=False, encoding=62, fastDecode=True)
        return self.get_tags_around(packed)

@register.tag
def jscript(parser, token):
    """
    Based on jspacker by Dean Edwards,
    Python port by Florian Schulze: http://www.crowproductions.de/repos/main/public/packer/jspacker.py
    Packs javascript

    Example usage::

        {% jscript %}
        var a = 1;
        var b = 2;
        var c = 3;
        alert(a+b);
        {% endjscript %}

    This example would return this script::

    <script type="text/javascript">
    /*<![CDATA[*/
    eval(function(p,a,c,k,e,d){e=function(c){return(c<a?"":e(parseInt(c/a)))+((c=c%a)>35?String.fromCharCode(c+29):c.toString(36))};if(!''.replace(/^/,String)){while(c--)d[c]=k[c]||c;k=[function(e){return d[e]}];e=function(){return'\\w+'};c=1};while(c--)if(k[c])p=p.replace(new RegExp("\\b"+e(c)+"\\b","g"),k[c]);return p}('0 5 = 1;\n        0 4 = 2;\n        0 7 = 3;\n        6(5+4);\n',8,8,'var||||b|a|alert|c'.split('|'),0,{}))
    /*]]>*/
    </script>
    """
    nodelist = parser.parse(('endjscript',))
    parser.delete_first_token()
    split = token.split_contents()
    return PackedJSNode(nodelist, ready=(len(split) >= 2 and split[1] == 'ready'))


'''
Filter for JSON data
'''

from django.core.serializers import json, serialize
from django.utils import simplejson
from django.utils.safestring import mark_safe
from django.db.models.query import QuerySet

@register.filter(name='json')
def jsonify(object):
    if isinstance(object, QuerySet):
        return serialize('json', object)
    return mark_safe(simplejson.dumps(object, indent=2, cls=json.DjangoJSONEncoder, ensure_ascii=False))