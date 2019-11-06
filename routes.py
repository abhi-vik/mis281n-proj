from flask import request, redirect, session, jsonify, abort, render_template
import model
from util import delay, convert

router = {
    'login': delay('login.html', ['show_register']),
    'register': delay('register.html', []),
    'main': delay('main.html', ['is_regular', 'show_logout'], js='main.js'),
    'history': delay('history.html', ['is_regular', 'show_logout']),
    'report_one': delay('report_one.html', ['is_admin', 'show_logout']),
    'report_two': delay('report_two.html', ['is_admin', 'show_logout']),
    'report_three': delay('report_three.html', ['is_admin', 'show_logout']),
    'reset': delay('reset.html', ['is_admin', 'show_logout'])
}


def init(app):
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

        return router['login']()

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

        return router['register']()

    @app.route('/')
    def main():
        if 'user_id' not in session:
            return redirect('/login')

        if session['user_admin'] is True:
            return redirect('/reports?type=1')
        else:
            return router['main']()

    @app.route('/reports')
    def report():
        if 'user_id' not in session:
            return redirect('/login')

        if not session['user_admin']:
            return router['main']()

        report_type = request.args.get('type')

        if report_type == '2':
            return router['report_two']([], data=model.get_second_report())
        elif report_type == '3':
            return router['report_three']([], data=model.get_third_report())
        else:
            # assume default report
            return router['report_one']([], data=model.get_first_report())

    @app.route('/reset', methods=['GET', 'POST'])
    def reset():
        if 'user_id' not in session:
            return redirect('/login')

        if not session['user_admin']:
            return router['main']()

        if request.method == 'POST':
            model.reset()

            return redirect('/reports')

        return router['reset']()

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
            model.gift(session['user_id'], **data)
            return jsonify(success=True)
        except Exception:
            return abort(400)

    @app.route('/redeem', methods=['POST'])
    def redeem():
        data = request.get_json()

        try:
            model.redeem(session['user_id'], **data)
            return jsonify(success=True)
        except Exception:
            return abort(400)

    @app.route('/history')
    def history():
        if 'user_id' not in session:
            return redirect('/login')

        return router['history']([], data=model.history(session['user_id']))

    @app.route('/logout', methods=['POST'])
    def logout():
        if 'user_id' in session:
            del session['user_id']
            del session['user_admin']
            session.permanent = False

        return redirect('/login')
