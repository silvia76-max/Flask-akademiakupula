-- Script SQL para crear las tablas de lista de deseos y carrito
-- Ejecuta este script directamente en tu base de datos SQLite

-- Tabla para la lista de deseos
CREATE TABLE IF NOT EXISTS wishlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (course_id) REFERENCES courses (id)
);

-- Tabla para el carrito
CREATE TABLE IF NOT EXISTS cart (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (course_id) REFERENCES courses (id)
);

-- Índices para mejorar el rendimiento
CREATE INDEX IF NOT EXISTS idx_wishlist_user_id ON wishlist (user_id);
CREATE INDEX IF NOT EXISTS idx_wishlist_course_id ON wishlist (course_id);
CREATE INDEX IF NOT EXISTS idx_cart_user_id ON cart (user_id);
CREATE INDEX IF NOT EXISTS idx_cart_course_id ON cart (course_id);
