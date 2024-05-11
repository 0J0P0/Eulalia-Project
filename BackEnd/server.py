"""
Module: server.py
Author: JP Zaldivar  && Noa Mediavilla
Date: April 20, 2024

Description:
This module contains the server that will receive messages from the frontend and return a response.

Contents:
- store_chat_message: Function to store the message received in a postgreSQL database.
- store_contact_messages: Function to store the contact messages received in a postgreSQL database.
- process_chat_message: Function to process the message received and return a response.
"""


import os
from flask_cors import CORS
from flask import Flask, request, jsonify


from EulaliaGPT.eulalia import get_response
from DataBase.connection import create_connection


app = Flask(__name__)
CORS(app)  # Allow CORS for all routes


@app.route('/login', methods=['POST'])
def login():
    """
    Authenticate user based on provided credentials.

    Expects JSON data with 'username' and 'password' fields.

    Returns:
    JSON: Authentication result.
    """
    # Get the JSON data from the request
    data = request.get_json()
    # Extract username and password from the JSON data
    username = data.get('username')
    password = data.get('password')

    # Check if username or password is missing
    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    try:
        # Create a connection to your PostgreSQL database
        conn, cur = create_connection()

        # Execute the SQL query to check if the username and password match
        cur.execute(f"SELECT * FROM {os.getenv('LOGIN_TABLE')} WHERE username = %s AND password = %s;", (username, password))
        user = cur.fetchone()

        # Commit changes and close the cursor and connection
        conn.commit()
        cur.close()
        conn.close()

        # Check if user exists (authentication successful)
        if user:
            return jsonify({"success": True, "message": "Authentication successful"})
        else:
            return jsonify({"success": False, "message": "Authentication failed"})
    except Exception as e:
        # Handle any errors that occur during the process
        print(f"Error authenticating user: {e}")
        return jsonify({"success": False, "message": "Authentication failed"}), 500


def store_chat_message(data):
    """
    Store the message received in a postgreSQL database.

    Parameters
    ----------
    response : dict
        Data received.
    """
    
    try:
        conn, cur = create_connection()
        # print(data)

        last_message = data['messages'][-2]
        last_reply = data['messages'][-1]
        # print(last_message)
        # print(last_reply)

        user_message = last_message['message']
        chat_message = last_reply['message']
        user_conv = last_message['conv_title']
        # print(user_message)
        # print(chat_message)
        # print(user_conv)


        cur.execute(
            f'''INSERT INTO {os.getenv("DATABASE_MESSAGES_TABLE")} (user_id, user_message, chat_message, user_conv, user_conv_id) VALUES (%s, %s, %s, %s, %s);''',
            ('admin@eulalia.com', user_message, chat_message, user_conv, 1))

        conn.commit()
        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error storing message: {e}")


@app.route('/api/store_contact_messages', methods=['POST'])
def store_contact_messages() -> dict:
    """
    Store the contact messages received in a postgreSQL database.

    Returns
    -------
    dict
        Response message with log information.
    """

    data = request.get_json()

    try:
        conn, cur = create_connection()

        cur.execute(
            f'''INSERT INTO {os.getenv("DATABASE_CONTACT_TABLE")} (user_id, user_name, user_contact_message) VALUES (%s, %s, %s);''',
            (data['email'], data['name'], data['message'])
        )

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"log": "Message stored successfully"})
    except Exception as e:
        print(f"Error storing contact message: {e}")
        return jsonify({"log": "Error storing message"})


@app.route('/api/process_chat_message', methods=['POST'])
def process_chat_message() -> dict:
    """
    Process the message received and return a response.

    Returns
    -------
    dict
        Response message.
    """
    
    data = request.get_json()
    
    response = get_response(data)

    # store_chat_message(data)

    return jsonify(response)


# @app.route('/api/refresh_history', methods=['POST'])
# def new_chat():
#     """
#     Refresh history
#     Returns last conversation title created and id --> for later identification
#     """

#     try:
#         conn, cur = create_connection()


#         # FES LA CERCA AMB COMANDA SQL DELS NOMS DE LES CONVERSES --> A PLANTEJAR (SELECT DISTINC FROM)
#         # cur.execute(
        #     f'''INSERT INTO {os.getenv("DATABASE_CONTACT_TABLE")} (user_id, user_name, user_contact_message) VALUES (%s, %s, %s);''',
        #     (data['email'], data['name'], data['message'])
        # )

        # conn.commit()
        # cur.close()
        # conn.close()

#         return jsonify({"log": "Message stored successfully"}) # CAMVIAR EL RETURN (VOLEM QUE RETORNI EL NOM I ID)
#     except Exception as e:
#         print(f"Error getting last conversation: {e}")
#         return jsonify({"log": "Error getting last conversation"})



if __name__ == '__main__':
    app.run(debug=True)
