import mysql.connector
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import urllib.parse

# ✅ MySQL Database Connection
def get_db_connection():
    """Create and return a new database connection."""
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Change this if needed
        password="",  # Set MySQL password if required
        database="dental_clinic"
    )

class SimpleHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        """Handle GET request - Fetch all reservations"""
        if self.path == "/api/reservations":
            try:
                db = get_db_connection()
                cursor = db.cursor()
                cursor.execute("SELECT id, name, email, date, time, regular, payment, transaction FROM reservations")
                reservations = cursor.fetchall()
                
                result = [
                    {
                        "id": r[0],  # Include ID for updates/deletions
                        "name": r[1], 
                        "email": r[2], 
                        "date": str(r[3]), 
                        "time": str(r[4]),
                        "regular": r[5], 
                        "payment": r[6], 
                        "transaction": r[7]
                    } 
                    for r in reservations
                ]

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")  # ✅ Enable CORS
                self.end_headers()
                self.wfile.write(json.dumps(result).encode("utf-8"))
            
            except Exception as e:
                self.send_error(500, "Server Error: " + str(e))
            
            finally:
                cursor.close()
                db.close()

    def do_POST(self):
        """Handle POST request - Add a new reservation"""
        if self.path == "/api/reservations":
            try:
                content_length = int(self.headers["Content-Length"])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode("utf-8"))

                db = get_db_connection()
                cursor = db.cursor()
                sql = "INSERT INTO reservations (name, email, date, time, regular, payment, transaction) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                values = (data["name"], data["email"], data["date"], data["time"], data["regular"], data["payment"], data["transaction"])
                cursor.execute(sql, values)
                db.commit()

                self.send_response(201)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")  # ✅ Enable CORS
                self.end_headers()
                self.wfile.write(json.dumps({"message": "Reservation added successfully"}).encode("utf-8"))
            
            except json.JSONDecodeError:
                self.send_error(400, "Invalid JSON data")
            
            except Exception as e:
                self.send_error(500, "Server Error: " + str(e))
            
            finally:
                cursor.close()
                db.close()

    def do_DELETE(self):
        """Handle DELETE request - Remove a reservation"""
        if self.path.startswith("/api/reservations/"):
            try:
                reservation_id = self.path.split("/")[-1]
                db = get_db_connection()
                cursor = db.cursor()
                sql = "DELETE FROM reservations WHERE id = %s"
                cursor.execute(sql, (reservation_id,))
                db.commit()

                if cursor.rowcount > 0:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(json.dumps({"message": "Reservation deleted successfully"}).encode("utf-8"))
                else:
                    self.send_error(404, "Reservation not found")

            except Exception as e:
                self.send_error(500, "Server Error: " + str(e))
            
            finally:
                cursor.close()
                db.close()

    def do_PUT(self):
        """Handle PUT request - Update an existing reservation"""
        if self.path.startswith("/api/reservations/"):
            try:
                reservation_id = self.path.split("/")[-1]
                content_length = int(self.headers["Content-Length"])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode("utf-8"))

                db = get_db_connection()
                cursor = db.cursor()
                sql = "UPDATE reservations SET date = %s, time = %s WHERE id = %s"
                cursor.execute(sql, (data["date"], data["time"], reservation_id))
                db.commit()

                if cursor.rowcount > 0:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(json.dumps({"message": "Reservation updated successfully"}).encode("utf-8"))
                else:
                    self.send_error(404, "Reservation not found")

            except json.JSONDecodeError:
                self.send_error(400, "Invalid JSON data")
            
            except Exception as e:
                self.send_error(500, "Server Error: " + str(e))
            
            finally:
                cursor.close()
                db.close()

    def do_OPTIONS(self):
        """Handle preflight CORS requests"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

# ✅ Run the server
server_address = ("", 5000)
httpd = HTTPServer(server_address, SimpleHandler)
print("🚀 Server running on http://localhost:5000 ...")
httpd.serve_forever()
