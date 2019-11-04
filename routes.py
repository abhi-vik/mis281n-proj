from flask import request, redirect, session, jsonify, abort
import model
from util import delay, convert

router = {
    'login': delay('login.html', ['show_register']),
    'register': delay('register.html', []),
    'main': delay('main.html', ['show_logout'], js='main.js')
}


def add(app):
    with app.app_context():
        model.init_app(app)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if 'user_id' in session:
            return redirect('/')

        if request.method == 'POST':
            data = request.form.to_dict(flat=True)

            result = model.authenticate(data['username'], data['password'])

            if isinstance(result, model.User):
                session.permanent = True
                session['user_id'] = result.id
                session['user_admin'] = result.admin
                return redirect('/')
            else:
                return router['login'](['invalid'])

        return router['login']([])

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if 'user_id' in session:
            return redirect('/')

        if request.method == 'POST':
            data = request.form.to_dict(flat=True)
            try:
                model.create_user(data)
            except ValueError:
                return router['register'](['invalid'])
            except Exception:
                return router['register'](['other'])

            return router['login'](['success'])

        return router['register']([])

    @app.route('/')
    def main():
        if 'user_id' not in session:
            return redirect('/login')

        return router['main']([])

    @app.route('/details')
    def details():
        if 'user_id' not in session:
            return redirect('/login')

        user, usernames = model.details(session['user_id'])

        return {
            'user': convert(user),
            'usernames': usernames
        }

    @app.route('/gift', methods=['POST'])
    def gift():
        data = request.get_json()

        try:
            print(data)
            model.gift(session['user_id'], **data)
            return jsonify(success=True)
        except Exception:
            return abort(400)

    @app.route('/logout', methods=['POST'])
    def logout():
        if 'user_id' in session:
            del session['user_id']
            del session['user_admin']
            session.permanent = False

        return redirect('/login')

    return app
