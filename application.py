from app import app
import os

# Read PORT available on cloud server
port = int(os.environ.get('PORT', 8000))

if __name__ == '__main__':
    # Run the flask app
    app.run(host='0.0.0.0',port=port, debug=debug_flag)
