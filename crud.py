import psycopg2
from werkzeug.security import generate_password_hash
from datetime import datetime

class Database:
    def __init__(self, config: dict):
        self.config = {
            "host": config.get("host"),
            "dbname": config.get("database") or config.get("dbname"),
            "user": config.get("user"),
            "password": config.get("password"),
            "port": config.get("port"),
        }

    # ---------- helpers ----------
    def _get_conn(self):
        return psycopg2.connect(**self.config)

    # ---------- USERS ----------
    def get_user(self, username: str):
        conn = self._get_conn()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT id, username, password, role, nama, email, nohp
                FROM users
                WHERE username = %s
            """, (username,))
            return cur.fetchone()
        except Exception as e:
            print("get_user error:", e)
            return None
        finally:
            cur.close(); conn.close()

    def get_user_by_id(self, user_id: int):
        conn = self._get_conn()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT id, username, password, role, nama, email, nohp
                FROM users
                WHERE id = %s
            """, (user_id,))
            return cur.fetchone()
        except Exception as e:
            print("get_user_by_id error:", e)
            return None
        finally:
            cur.close(); conn.close()

    def create_user(self, username, password, role, nama, email, nohp):
        conn = self._get_conn()
        cur = conn.cursor()
        try:
            hashed = generate_password_hash(password)
            cur.execute("""
                INSERT INTO users (username, password, role, nama, email, nohp)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (username, hashed, role, nama, email, nohp))
            user_id = cur.fetchone()[0]
            conn.commit()
            return user_id
        except Exception as e:
            print("create_user error:", e)
            conn.rollback()
            return None
        finally:
            cur.close(); conn.close()

    def update_user(self, user_id, username, nama, email, nohp, role=None, password=None):
        """
        Update profil. Jika password diberikan (bukan None/''), akan di-hash.
        `role` optional: jika None tidak diubah.
        """
        conn = self._get_conn()
        cur = conn.cursor()
        try:
            params = [username, nama, email, nohp]
            sets   = ["username=%s", "nama=%s", "email=%s", "nohp=%s"]

            if role is not None:
                sets.append("role=%s")
                params.append(role)

            if password:
                sets.append("password=%s")
                params.append(generate_password_hash(password))

            q = f"UPDATE users SET {', '.join(sets)}, updated_at=CURRENT_TIMESTAMP WHERE id=%s"
            params.append(user_id)

            cur.execute(q, tuple(params))
            conn.commit()
            return True
        except Exception as e:
            print("update_user error:", e)
            conn.rollback()
            return False
        finally:
            cur.close(); conn.close()

    def delete_user(self, user_id: int):
        conn = self._get_conn()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM users WHERE id=%s", (user_id,))
            conn.commit()
            return True
        except Exception as e:
            print("delete_user error:", e)
            conn.rollback()
            return False
        finally:
            cur.close(); conn.close()

    def update_user_password_by_email(self, email, new_hashed_password):
        """
        Dipakai oleh reset password di main.py (sudah menerima password yang SUDAH di-hash).
        """
        conn = self._get_conn()
        cur = conn.cursor()
        try:
            cur.execute("UPDATE users SET password=%s, updated_at=CURRENT_TIMESTAMP WHERE email=%s",
                        (new_hashed_password, email))
            conn.commit()
            return True
        except Exception as e:
            print("update_user_password_by_email error:", e)
            conn.rollback()
            return False
        finally:
            cur.close(); conn.close()

    def check_email_exists(self, email):
        conn = self._get_conn()
        cur = conn.cursor()
        try:
            cur.execute("SELECT 1 FROM users WHERE email=%s LIMIT 1", (email,))
            return cur.fetchone() is not None
        except Exception as e:
            print("check_email_exists error:", e)
            return False
        finally:
            cur.close(); conn.close()

    def check_email_exists_for_update(self, email, exclude_id):
        conn = self._get_conn()
        cur = conn.cursor()
        try:
            cur.execute("SELECT 1 FROM users WHERE email=%s AND id<>%s LIMIT 1", (email, exclude_id))
            return cur.fetchone() is not None
        except Exception as e:
            print("check_email_exists_for_update error:", e)
            return False
        finally:
            cur.close(); conn.close()

    def check_username_exists(self, username, exclude_id=None):
        conn = self._get_conn()
        cur = conn.cursor()
        try:
            if exclude_id:
                cur.execute("SELECT 1 FROM users WHERE username=%s AND id<>%s LIMIT 1",
                            (username, exclude_id))
            else:
                cur.execute("SELECT 1 FROM users WHERE username=%s LIMIT 1", (username,))
            return cur.fetchone() is not None
        except Exception as e:
            print("check_username_exists error:", e)
            return False
        finally:
            cur.close(); conn.close()

    def count_users(self):
        conn = self._get_conn()
        cur = conn.cursor()
        try:
            cur.execute("SELECT COUNT(*) FROM users")
            row = cur.fetchone()
            return row[0] if row else 0
        except Exception as e:
            print("count_users error:", e)
            return 0
        finally:
            cur.close(); conn.close()

    def read_all_users(self):
        conn = self._get_conn()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT id, username, role, nama, email, nohp, created_at, updated_at
                FROM users
                ORDER BY id
            """)
            return cur.fetchall()
        except Exception as e:
            print("read_all_users error:", e)
            return []
        finally:
            cur.close(); conn.close()

    # ---------- BARANG ----------
    def create_barang(self, nama_barang, harga, deskripsi):
        conn = self._get_conn()
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO barang (nama_barang, harga, deskripsi)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (nama_barang, harga, deskripsi))
            barang_id = cur.fetchone()[0]
            conn.commit()
            return barang_id
        except Exception as e:
            print("create_barang error:", e)
            conn.rollback()
            return None
        finally:
            cur.close(); conn.close()

    def get_barang_by_id(self, barang_id):
        conn = self._get_conn()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT id, nama_barang, harga, deskripsi
                FROM barang
                WHERE id=%s
            """, (barang_id,))
            return cur.fetchone()
        except Exception as e:
            print("get_barang_by_id error:", e)
            return None
        finally:
            cur.close(); conn.close()

    def get_data_barang_nama_harga(self, nama_barang, harga):
        conn = self._get_conn()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT id, nama_barang, harga
                FROM barang
                WHERE nama_barang=%s AND harga=%s
            """, (nama_barang, harga))
            return cur.fetchone()
        except Exception as e:
            print("get_data_barang_nama_harga error:", e)
            return None
        finally:
            cur.close(); conn.close()

    def read_all_barang(self):
        conn = self._get_conn()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT id, nama_barang, harga, deskripsi,
                       to_char(created_at, 'DD-MM-YYYY HH24:MI') AS created,
                       to_char(updated_at, 'DD-MM-YYYY HH24:MI') AS updated
                FROM barang
                ORDER BY id
            """)
            return cur.fetchall()
        except Exception as e:
            print("read_all_barang error:", e)
            return []
        finally:
            cur.close(); conn.close()

    def update_barang(self, barang_id, nama_barang, harga, deskripsi):
        conn = self._get_conn()
        cur = conn.cursor()
        try:
            cur.execute("""
                UPDATE barang
                SET nama_barang=%s, harga=%s, deskripsi=%s,
                    updated_at=CURRENT_TIMESTAMP
                WHERE id=%s
                RETURNING id
            """, (nama_barang, harga, deskripsi, barang_id))
            row = cur.fetchone()
            conn.commit()
            return row[0] if row else None
        except Exception as e:
            print("update_barang error:", e)
            conn.rollback()
            return None
        finally:
            cur.close(); conn.close()

    def delete_barang(self, barang_id):
        conn = self._get_conn()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM barang WHERE id=%s RETURNING id", (barang_id,))
            row = cur.fetchone()
            conn.commit()
            return row[0] if row else None
        except Exception as e:
            print("delete_barang error:", e)
            conn.rollback()
            return None
        finally:
            cur.close(); conn.close()

    # ---------- CART ----------
    def _get_or_create_cart(self, user_id: int):
        conn = self._get_conn(); cur = conn.cursor()
        try:
            cur.execute("SELECT id FROM carts WHERE user_id=%s", (user_id,))
            row = cur.fetchone()
            if row:
                return row[0]
            cur.execute("INSERT INTO carts (user_id) VALUES (%s) RETURNING id", (user_id,))
            cid = cur.fetchone()[0]
            conn.commit()
            return cid
        except Exception as e:
            print("_get_or_create_cart error:", e); conn.rollback(); return None
        finally:
            cur.close(); conn.close()

    def add_to_cart(self, user_id: int, barang_id: int, qty: int = 1):
        conn = self._get_conn(); cur = conn.cursor()
        try:
            # ambil harga saat ini
            cur.execute("SELECT harga FROM barang WHERE id=%s", (barang_id,))
            r = cur.fetchone()
            if not r: return False
            harga = r[0]

            # pastikan cart ada
            cur.execute("SELECT id FROM carts WHERE user_id=%s", (user_id,))
            row = cur.fetchone()
            cart_id = row[0] if row else None
            if not cart_id:
                cur.execute("INSERT INTO carts (user_id) VALUES (%s) RETURNING id", (user_id,))
                cart_id = cur.fetchone()[0]

            # tambah / akumulasi qty
            cur.execute("""
                INSERT INTO cart_items (cart_id, barang_id, qty, price_at_add)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (cart_id, barang_id)
                DO UPDATE SET qty = cart_items.qty + EXCLUDED.qty
            """, (cart_id, barang_id, qty, harga))
            conn.commit(); return True
        except Exception as e:
            print("add_to_cart error:", e); conn.rollback(); return False
        finally:
            cur.close(); conn.close()

    def get_cart_items(self, user_id: int):
        conn = self._get_conn(); cur = conn.cursor()
        try:
            cur.execute("""
                SELECT ci.id, ci.barang_id, b.nama_barang, ci.qty, ci.price_at_add,
                       (ci.qty * ci.price_at_add) AS subtotal
                FROM carts c
                JOIN cart_items ci ON ci.cart_id=c.id
                JOIN barang b ON b.id=ci.barang_id
                WHERE c.user_id=%s
                ORDER BY ci.id
            """, (user_id,))
            items = cur.fetchall()
            total = sum([row[5] for row in items]) if items else 0
            return items, total
        except Exception as e:
            print("get_cart_items error:", e); return [], 0
        finally:
            cur.close(); conn.close()

    def update_cart_qty(self, item_id: int, qty: int, user_id: int):
        conn = self._get_conn(); cur = conn.cursor()
        try:
            if qty <= 0:
                cur.execute("""
                    DELETE FROM cart_items
                    WHERE id=%s AND cart_id IN (SELECT id FROM carts WHERE user_id=%s)
                """, (item_id, user_id))
            else:
                cur.execute("""
                    UPDATE cart_items
                    SET qty=%s
                    WHERE id=%s AND cart_id IN (SELECT id FROM carts WHERE user_id=%s)
                """, (qty, item_id, user_id))
            conn.commit(); return True
        except Exception as e:
            print("update_cart_qty error:", e); conn.rollback(); return False
        finally:
            cur.close(); conn.close()

    def remove_cart_item(self, item_id: int, user_id: int):
        conn = self._get_conn(); cur = conn.cursor()
        try:
            cur.execute("""
                DELETE FROM cart_items
                WHERE id=%s AND cart_id IN (SELECT id FROM carts WHERE user_id=%s)
            """, (item_id, user_id))
            conn.commit(); return True
        except Exception as e:
            print("remove_cart_item error:", e); conn.rollback(); return False
        finally:
            cur.close(); conn.close()

    def clear_cart(self, user_id: int):
        conn = self._get_conn(); cur = conn.cursor()
        try:
            cur.execute("""
                DELETE FROM cart_items
                WHERE cart_id IN (SELECT id FROM carts WHERE user_id=%s)
            """, (user_id,))
            conn.commit(); return True
        except Exception as e:
            print("clear_cart error:", e); conn.rollback(); return False
        finally:
            cur.close(); conn.close()

    # ---------- ORDERS ----------
    def create_order_from_cart(self, user_id: int, payment_method: str, shipping_address: str | None):
        conn = self._get_conn(); cur = conn.cursor()
        try:
            # ambil isi cart
            cur.execute("""
                SELECT ci.barang_id, b.nama_barang, ci.qty, ci.price_at_add
                FROM carts c
                JOIN cart_items ci ON ci.cart_id=c.id
                JOIN barang b ON b.id=ci.barang_id
                WHERE c.user_id=%s
            """, (user_id,))
            rows = cur.fetchall()
            if not rows: return None

            total = sum([r[2]*r[3] for r in rows])

            cur.execute("""
                INSERT INTO orders (user_id, status, total, payment_method, payment_status, shipping_address)
                VALUES (%s, 'baru', %s, %s, %s, %s)
                RETURNING id
            """, (user_id, total, payment_method, 'pending', shipping_address))
            order_id = cur.fetchone()[0]

            for barang_id, nama, qty, harga in rows:
                cur.execute("""
                    INSERT INTO order_items (order_id, barang_id, nama_snapshot, harga_snapshot, qty)
                    VALUES (%s, %s, %s, %s, %s)
                """, (order_id, barang_id, nama, harga, qty))

            # kosongkan cart
            cur.execute("""
                DELETE FROM cart_items
                WHERE cart_id IN (SELECT id FROM carts WHERE user_id=%s)
            """, (user_id,))

            conn.commit()
            return order_id
        except Exception as e:
            print("create_order_from_cart error:", e); conn.rollback(); return None
        finally:
            cur.close(); conn.close()

    def list_orders(self, status: str | None = None):
        conn = self._get_conn(); cur = conn.cursor()
        try:
            if status:
                cur.execute("""
                    SELECT id, user_id, status, total, payment_method, payment_status, created_at
                    FROM orders WHERE status=%s ORDER BY id DESC
                """, (status,))
            else:
                cur.execute("""
                    SELECT id, user_id, status, total, payment_method, payment_status, created_at
                    FROM orders ORDER BY id DESC
                """)
            return cur.fetchall()
        except Exception as e:
            print("list_orders error:", e); return []
        finally:
            cur.close(); conn.close()

    def get_order(self, order_id: int):
        conn = self._get_conn(); cur = conn.cursor()
        try:
            cur.execute("""
                SELECT id, user_id, status, total, payment_method, payment_status, shipping_address, created_at
                FROM orders WHERE id=%s
            """, (order_id,))
            order = cur.fetchone()
            cur.execute("""
                SELECT barang_id, nama_snapshot, harga_snapshot, qty
                FROM order_items WHERE order_id=%s
            """, (order_id,))
            items = cur.fetchall()
            return order, items
        except Exception as e:
            print("get_order error:", e); return None, []
        finally:
            cur.close(); conn.close()

    def update_order_status(self, order_id: int, new_status: str, payment_status: str | None = None):
        conn = self._get_conn(); cur = conn.cursor()
        try:
            sets = ["status=%s", "updated_at=CURRENT_TIMESTAMP"]
            params = [new_status]
            if payment_status is not None:
                sets.append("payment_status=%s"); params.append(payment_status)
            params.append(order_id)
            cur.execute(f"UPDATE orders SET {', '.join(sets)} WHERE id=%s", tuple(params))
            conn.commit(); return True
        except Exception as e:
            print("update_order_status error:", e); conn.rollback(); return False
        finally:
            cur.close(); conn.close()

    def list_user_orders(self, user_id: int):
        conn = self._get_conn(); cur = conn.cursor()
        try:
            cur.execute("""
                SELECT id, status, total, payment_method, payment_status, created_at
                FROM orders WHERE user_id=%s ORDER BY id DESC
            """, (user_id,))
            return cur.fetchall()
        except Exception as e:
            print("list_user_orders error:", e); return []
        finally:
            cur.close(); conn.close()
def get_cart_count(self, user_id: int) -> int:
    conn = self._get_conn(); cur = conn.cursor()
    try:
        cur.execute("""
            SELECT COALESCE(SUM(ci.qty), 0)
            FROM carts c
            LEFT JOIN cart_items ci ON ci.cart_id = c.id
            WHERE c.user_id = %s
        """, (user_id,))
        row = cur.fetchone()
        return int(row[0] or 0)
    except Exception as e:
        print("get_cart_count error:", e); return 0
    finally:
        cur.close(); conn.close()



# ---------- bootstrap tables ----------

def create_tables(db_config):
    conn = psycopg2.connect(
        host=db_config.get("host"),
        dbname=db_config.get("database") or db_config.get("dbname"),
        user=db_config.get("user"),
        password=db_config.get("password"),
        port=db_config.get("port"),
    )
    cur = conn.cursor()
    try:
        # users
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role VARCHAR(10) NOT NULL,
                nama TEXT NOT NULL,
                email TEXT NOT NULL,
                nohp TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # barang
        cur.execute("""
            CREATE TABLE IF NOT EXISTS barang (
                id SERIAL PRIMARY KEY,
                nama_barang TEXT NOT NULL,
                harga NUMERIC NOT NULL,
                deskripsi TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # carts
        cur.execute("""
            CREATE TABLE IF NOT EXISTS carts (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (user_id)
            )
        """)

        # cart_items
        cur.execute("""
            CREATE TABLE IF NOT EXISTS cart_items (
                id SERIAL PRIMARY KEY,
                cart_id INTEGER NOT NULL REFERENCES carts(id) ON DELETE CASCADE,
                barang_id INTEGER NOT NULL REFERENCES barang(id) ON DELETE CASCADE,
                qty INTEGER NOT NULL CHECK (qty > 0),
                price_at_add NUMERIC NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (cart_id, barang_id)
            )
        """)

        # orders
        cur.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                status TEXT NOT NULL DEFAULT 'baru',
                total NUMERIC NOT NULL DEFAULT 0,
                payment_method TEXT,
                payment_status TEXT,
                shipping_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # order_items
        cur.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id SERIAL PRIMARY KEY,
                order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
                barang_id INTEGER REFERENCES barang(id) ON DELETE SET NULL,
                nama_snapshot TEXT NOT NULL,
                harga_snapshot NUMERIC NOT NULL,
                qty INTEGER NOT NULL CHECK (qty > 0)
            )
        """)

        # payments (opsional)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id SERIAL PRIMARY KEY,
                order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
                method TEXT,
                amount NUMERIC NOT NULL,
                provider TEXT,
                va_number TEXT,
                status TEXT,
                paid_at TIMESTAMP,
                raw JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
    except Exception as e:
        print("create_tables error:", e)
        conn.rollback()
    finally:
        cur.close(); conn.close()
