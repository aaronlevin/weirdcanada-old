# coding=utf-8

import re
import datetime
from flask import request, url_for, redirect, flash
from flask.ext.wtf import Form 
from flask.ext.wtf import DateTimeField
from flask.ext.wtf import FieldList
from flask.ext.wtf.file import FileField
from flask.ext.wtf import FormField
from flask.ext.wtf import HiddenField
from flask.ext.wtf import IntegerField
from flask.ext.wtf import PasswordField
from flask.ext.wtf import SelectField
from flask.ext.wtf import TextAreaField
from flask.ext.wtf import TextField
from flask.ext.wtf.html5 import URLField
from flask.ext.wtf import validators
from flask.ext.wtf import ListWidget
from helpers import html_params, is_safe_url, get_redirect_target, make_nice
from models import User
from wtforms.widgets import HTMLString

# Widget

class FieldWidget(object):

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id',field.id)
        html = [u'<div class="control-group%s">' % (' error' if field.errors else '') ]
        html.append(u'<label for="%s" class="control-label">%s</label>' % (field.id, make_nice(field.short_name)))
        html.append(u'<div class="controls">')
        if field.type == 'TextField':
            html.append(u'<input type="text" class="input-xlarge" id="%s" name="%s">' % (field.id,make_nice(field.short_name)))
        elif field.type == 'TextAreaField':
            html.append(u'<textarea class="input-xlarge" id="%s" name="%s"></textarea>' % (field.id, make_nice(field.short_name)))
        elif field.type == 'DateTimeField':
            today = datetime.date.today().strftime('%Y-%m-%d')
            html.append(u'<input id="%s" type="text" value="%s" name="%s"><button class="btn" type="button"><i class="icon-calendar"></i></button>' % (field.id,today, make_nice(field.short_name)))
        elif field.type == 'SelectField':
            html.append(u'<select id="%s" name="%s">' % (field.id, make_nice(field.short_name)))
            for index, (value, label, select) in enumerate(field.iter_choices()):
                html.append(u'<option value="%s">%s</option>' % (value, label))
            html.append(u'</select>')
        elif field.type == 'FileField':
            html.append(u'<input id="%s" name="%s" type="file">' % (field.id, make_nice(field.short_name)))
        elif field.type == 'URLField':
            html.append(u'<input id="%s" type="url" name="%s">' % (field.id, make_nice(field.short_name)))

        # render errors
        if field.errors:
            html.append(u'<span class="help-inline"><ul>')
            for error in field.errors:
                html.append(u'<li>%s</li>' % (error))
            html.append(u'</ul></span>')
        html.append(u'</div></div>')
        return HTMLString(u''.join(html))

class DupeListWidget(object):
    """
    Renders a list of fields as a `ul` or `ol` list.

    This is used for FieldList fields. It does not handle rendering any field. Merely listing them.
    """
    def __init__(self, html_tag='ul', prefix_label=True):
        assert html_tag in ('ol','ul')
        self.html_tag = html_tag
        self.prefix_label = prefix_label

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id',field.id)
        html = [u'<div class="field_dupe" id="%s-dupe-0">' % (field.id)]
        for subfield in field:
            html.append(u'%s' % (subfield()))
        html.append(u'</div>')
        html.append(u'<div class="form-actions" ><input value="+ %s" type="button" class="btn btn-inverse" id="%s-click_dupe">  <input value="- %s" type="button" class="btn btn-inverse" id="%s-remove"></div>' % (make_nice(field.short_name), field.id,make_nice(field.short_name), field.id))
        return HTMLString(u''.join(html))

class FormFieldWidget(object):

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        tmp_hidden = u''
        html = [u'<div class="well"><fieldset><legend>%s</legend>' % (make_nice(field.short_name)) ]
        for subfield in field:
            if subfield.type == 'CSRFTokenField' or subfield.type == 'HiddenField':
                tmp_hidden += u'<div style="display:none;">%s</div>' % (subfield())
            else:
                html.append(u'%s' % (subfield()))
        if tmp_hidden is not '':
            html.append(tmp_hidden)
        html.append(u'</fieldset></div>')
        return HTMLString(u''.join(html))

# Forms

class RedirectForm(Form):
    next_url = HiddenField()

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        if not self.next_url.data:
            self.next_url.data = get_redirect_target() or ''

    def redirect(self, endpoint='index', **values):
        if is_safe_url(self.next_url.data):
            return redirect(self.next_url.data)
        target = get_redirect_target()
        return redirect(target or url_for(endpoint, **values))

class LoginForm(RedirectForm):
    username = TextField('Username')
    password = PasswordField('Password')
    honey_pot = HiddenField('Location')

    def validate_honey_pot(form, field):
        if len(field.data) > 0:
            raise ValidationError('Get out of my honey!')

class GeoForm(Form):
    city = TextField('City', widget=FieldWidget())
    province = SelectField(
        u'Province',
        choices = [
            ('British Columbia', 'British Columbia'),
            ('Alberta','Alberta'),
            ('Saskatchewan', 'Saskatchewan'),
            ('Manitoba','Manitoba'),
            ('Ontario','Ontario'),
            ('Quebec','Quebec'),
            ('Nova-scotia','Nova Scotia'),
            ('Prince Edward Island','Prince Edward Island'),
            ('Newfoundland','Newfoundland and Labrador'),
            ('Yukon','Yukon'),
            ('Nunavut','Nunavut'),
            ('Northwest Territories','Northwest Territories'),
        ], widget=FieldWidget())
    country = SelectField(u'Country',choices=[('canada', 'Canada'),('usa','USA')], widget=FieldWidget())

class ImageForm(Form):
    image = FileField(u'Image', widget=FieldWidget())
    one_liner = TextField(u'One Liner', widget=FieldWidget())
    description = TextAreaField(u'Description', widget=FieldWidget())

    #def __init__(self):
     #   super(ImageForm).__init__(csrf_enabled=False)

class TrackForm(Form):
    mp3 = FileField(u'Music File', widget=FieldWidget())
    artist = TextField(u'Artist', widget=FieldWidget())
    name = TextField(u'Track Name', widget=FieldWidget())

class ArtistForm(Form):
    name = TextField('Artist Name', [validators.required()], widget=FieldWidget())
    url = URLField('Artist URL', [validators.URL(message='Invalid Artist URL, bro'), validators.Optional()], widget=FieldWidget())
    geo = FormField(GeoForm, widget=FormFieldWidget())

class LabelForm(Form):
    name = TextField('Label Name', [validators.optional()], widget=FieldWidget())
    url = TextField('Label URL', [validators.URL(message='Invalid Label URL, bro'),validators.optional()], widget=FieldWidget())
    geo = FormField(GeoForm, widget=FormFieldWidget())

class AuthorForm(Form):
    name = TextField('Author Name', widget=FieldWidget())
    url = TextField('Author URL', [validators.URL(message='Invalid Author URL, bro'), validators.optional()], widget=FieldWidget())
    description = TextAreaField(u'Description', widget=FieldWidget())

class ReleaseForm(Form):
    title = TextField('Title', [validators.required()], widget=FieldWidget())
    cover_scan = FormField(ImageForm, widget=FormFieldWidget())
    support_images = FieldList(FormField(ImageForm, widget=FormFieldWidget()),widget=DupeListWidget(), min_entries=1)
    physical_format = SelectField(
        u'Format', 
        choices=[
            ('compact-disc', 'Compact Disc'),
            ('cassette', 'Cassette'),
            ('12-inch', '12" Vinyl LP'),
            ('10-inch', '10" Vinyl LP'),
            ('7-inch', '7"'),
            ('vhs', 'VHS')
        ]
    , widget=FieldWidget())
    release_date = DateTimeField('Date of Release (approx.)', widget=FieldWidget(), format='%Y-%m-%d')
    artists = FieldList(FormField(ArtistForm, widget=FormFieldWidget()), min_entries=1, widget=DupeListWidget())
    labels = FieldList(FormField(LabelForm, widget=FormFieldWidget()), min_entries=1, widget=DupeListWidget())

class ContentForm(Form):
    language = SelectField(u'Language', choices=[
        ('english', 'English'),
        ('french', 'French'),
    ], widget=FieldWidget())
    from_the = TextField(u'From The ... Of', widget=FieldWidget())
    text = TextAreaField(u'Content', widget=FieldWidget())

class PostForm(Form):
    release = FormField(ReleaseForm, widget=FormFieldWidget(), default='Release')
    contents = FieldList(FormField(ContentForm,widget=FormFieldWidget()), widget=DupeListWidget(), min_entries=1)
    section = SelectField(
        u'Section', 
        choices=[
            ('new-canadiana','New Canadiana'), 
            ('departures', 'Departures Revisited'), 
            ('fest', 'Festivities'),
            ('wyrd','Wyrd')
        ],
        widget=FieldWidget())
    authors = FieldList(SelectField(
        u'Author',
        choices=[
            ('Aaron Levin', 'Aaron Levin'),
            ('Jesse Locke', 'Jesse Locke'),
        ],
        widget=FieldWidget()),widget=DupeListWidget(), min_entries=1)
    publish_date = DateTimeField(u'Publish On', format='%Y-%m-%d', widget=FieldWidget())
    tracks = FieldList(FormField(TrackForm, widget=FormFieldWidget()),min_entries=1, widget=DupeListWidget())
    tags = TextField(u'Tags (delimiter=\';\')', widget=FieldWidget())


