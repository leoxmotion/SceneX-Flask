from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SubmitField, PasswordField, TextAreaField, FileField, SelectField, DateTimeField, IntegerField, DateField, TimeField, DateTimeLocalField, MultipleFileField, DecimalField, HiddenField
from wtforms.validators import DataRequired, Email, Length 
from flask_wtf.file import FileAllowed, FileRequired

class LoginForm(FlaskForm):
    usermail = EmailField("Email", validators=[Email('This is not an email!')])
    userpass = PasswordField("Password", validators=[DataRequired('Password field cannot be empty')])
    login = SubmitField("Login")

class ProfileForm(FlaskForm):
    fullname = StringField('Fullname')
    username = StringField('Username')
    bio= TextAreaField('Bio')
    state= SelectField('State', coerce=int)
    profile_pic = FileField('Upload Event Banner',validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images Only')])

class EventForm(FlaskForm):
    name = StringField('Event Name', validators=[DataRequired()])
    description = TextAreaField('Event Description', validators=[DataRequired()])
    banner = FileField('Upload Event Banner',validators=[FileRequired(), FileAllowed(['jpg', 'jpeg', 'png'], 'Images Only')])
    address = TextAreaField('Event Address')
    map_link = TextAreaField('Google Map Link')
    lga_id = SelectField('Local Government', validators=[DataRequired(message='Local Government is required')], coerce=int)
    state_id = SelectField('State', validators=[DataRequired(message='State is required')], coerce=int)
    cat_id = SelectField('Category', validators=[DataRequired(message='Category is required')], coerce=int)
    comm_id = SelectField('Community')
    event_start = DateTimeLocalField('Event Starts', validators=[DataRequired(message='Event start time is required')])
    event_end = DateTimeLocalField('Event Ends')
    ticket = SelectField('Ticket Type')
    vip_price = IntegerField('Ticket Price')
    table_price = IntegerField('Ticket Price')
    free_capacity = IntegerField('Free Capacity')
    vip_capacity = IntegerField('Vip Capacity')
    table_capacity = IntegerField('Table Capacity')
    lineup = SelectField('Role')
    lineup_name = StringField('Performer Name')
    submit = SubmitField('Publish')
    
    
class PostForm(FlaskForm):
   
    content = TextAreaField('Event Description', validators=[DataRequired()])
    media = FileField('Upload Event Banner',validators=[FileRequired(), FileAllowed(['jpg', 'jpeg', 'png'], 'Images Only')])
    event_id = SelectField('Local Government', validators=[DataRequired()], coerce=int)
    submit = SubmitField('Post')
    
class CommentForm(FlaskForm):
    comment = TextAreaField("Comment", validators=[DataRequired()])
    submit = SubmitField('Post')

class CommForm(FlaskForm):
    name = StringField('Community Name', validators=[DataRequired()])
    description = TextAreaField('Community Description', validators=[DataRequired()])
    banner = FileField('Upload Community Banner',validators=[FileRequired(), FileAllowed(['jpg', 'jpeg', 'png'], 'Images Only')])
    cat_id = SelectField('Category', validators=[DataRequired()], coerce=int)
    submit = SubmitField('Create Community')
    
class TicketForm(FlaskForm):

    ticket_id = HiddenField()

    name = StringField(
        "Ticket Name",
        validators=[DataRequired()]
    )

    category = SelectField(
        "Category",
        choices=[
            ("free","Free"),
            ("paid","Paid"),
            ("table","Table")
        ]
    )

    description = TextAreaField("Description")

    price = DecimalField(
        "Price",
        default=0
    )

    quantity = IntegerField(
        "Quantity",
        validators=[DataRequired()]
    )

    max_per_order = IntegerField(
        "Maximum Per Order",
        default=10
    )

    seats_per_ticket = IntegerField(
        "Seats Per Ticket",
        default=1
    )

    sales_start = DateTimeLocalField(
        "Sales Start",
        format="%Y-%m-%dT%H:%M"
    )

    sales_end = DateTimeLocalField(
        "Sales End",
        format="%Y-%m-%dT%H:%M"
    )

    submit = SubmitField("Add Ticket")