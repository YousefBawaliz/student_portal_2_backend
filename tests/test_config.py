def test_config(app):
    """Test configuration loading"""
    assert app.config['TESTING'] is True
    assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///:memory:'
    assert 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']