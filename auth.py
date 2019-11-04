from flask_bcrypt import Bcrypt


class Authenticator:
    bcrypt = None

    def set_app(self, app):
        self.bcrypt = Bcrypt(app)

    def make_hash(self, val):
        return self.bcrypt.generate_password_hash(val)

    def check_hash(self, true, val):
        return self.bcrypt.check_password_hash(true, val)
