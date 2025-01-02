import pytest
from app.auth.forms import validate_password_strength, validate_username, validate_name
from wtforms import Form, StringField, PasswordField

class DummyForm(Form):
    password = PasswordField('Password')
    username = StringField('Username')
    name = StringField('Name')

def test_password_validation():
    form = DummyForm()
    
    # Test valid password
    form.password.data = 'Test123!@#'
    assert validate_password_strength(form, form.password) is None
    
    # Test missing uppercase
    form.password.data = 'test123!@#'
    with pytest.raises(ValueError):
        validate_password_strength(form, form.password)
    
    # Test missing lowercase
    form.password.data = 'TEST123!@#'
    with pytest.raises(ValueError):
        validate_password_strength(form, form.password)
    
    # Test missing number
    form.password.data = 'TestABC!@#'
    with pytest.raises(ValueError):
        validate_password_strength(form, form.password)
    
    # Test missing special character
    form.password.data = 'Test12345'
    with pytest.raises(ValueError):
        validate_password_strength(form, form.password)

def test_username_validation():
    form = DummyForm()
    
    # Test valid username
    form.username.data = 'user123'
    assert validate_username(form, form.username) is None
    
    # Test username without numbers
    form.username.data = 'username'
    with pytest.raises(ValueError):
        validate_username(form, form.username)
    
    # Test username without letters
    form.username.data = '12345'
    with pytest.raises(ValueError):
        validate_username(form, form.username)

def test_name_validation():
    form = DummyForm()
    
    # Test valid name
    form.name.data = 'John'
    assert validate_name(form, form.name) is None
    
    # Test name with numbers
    form.name.data = 'John123'
    with pytest.raises(ValueError):
        validate_name(form, form.name)
    
    # Test name with special characters
    form.name.data = 'John!'
    with pytest.raises(ValueError):
        validate_name(form, form.name)
