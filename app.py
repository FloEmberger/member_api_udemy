from flask import Flask, g, request, jsonify
from database import get_db
import os
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

api_username = 'admin'
api_password = 'password'


def protected(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == api_username and auth.password == api_password:
            return f(*args, **kwargs)

        return jsonify({'message': 'Authentication failed'}), 403
    return decorated


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/member', methods=['GET'])
@protected
def get_members():
    db = get_db()
    members_cur = db.execute('Select id, name, email, level from members ORDER BY id ASC')
    members_result = members_cur.fetchall()

    list_members = []

    for member in members_result:
        members_dictionary = {'id': member['id'],
                              'name': member['name'],
                              'email': member['email'],
                              'level': member['level']
                              }

        list_members.append(members_dictionary)

    return jsonify({'members': list_members})


@app.route('/member/<int:member_id>', methods=['GET'])
@protected
def get_member(member_id):
    db = get_db()
    member_cur = db.execute('Select id, name, email, level from members where id = ?', [member_id])
    new_member = member_cur.fetchone()

    return jsonify({'member': {'id': new_member['id'],
                               'name': new_member['name'],
                               'email': new_member['email'],
                               'level': new_member['level']
                               }
                    })


@app.route('/member', methods=['POST'])
@protected
def add_member():
    new_member_data = request.get_json()
    name = new_member_data['name']
    email = new_member_data['email']
    level = new_member_data['level']

    db = get_db()
    db.execute('INSERT INTO members (name, email, level) VALUES(?, ?, ?)', [name, email, level])
    db.commit()

    member_cur = db.execute('Select id, name, email, level from members where name = ?', [name])
    new_member = member_cur.fetchone()

    return jsonify({'member': {'id': new_member['id'],
                               'name': new_member['name'],
                               'email': new_member['email'],
                               'level': new_member['level']
                                }
                    })


@app.route('/member/<int:member_id>', methods=['PUT', 'PATCH'])
@protected
def edit_member(member_id):
    new_member_data = request.get_json()
    name = new_member_data['name']
    email = new_member_data['email']
    level = new_member_data['level']

    db = get_db()
    db.execute(f'UPDATE members SET name = ?, email = ?, level = ? WHERE id = ?', [name, email, level, member_id])
    db.commit()

    member_update_cur = db.execute('SELECT * from members where id = ?', [member_id])
    member_update_result = member_update_cur.fetchone()

    return jsonify({'member': {'id': member_update_result['id'],
                               'name': member_update_result['name'],
                               'email': member_update_result['email'],
                               'level': member_update_result['level']
                               }})


@app.route('/member/<int:member_id>', methods=['DELETE'])
@protected
def delete_member(member_id):
    db = get_db()
    db.execute('DELETE from members where id = ?', [member_id])
    db.commit()

    return jsonify({'message': 'The member has been deleted!'})


if __name__ == '__main__':
    app.run(debug=True)