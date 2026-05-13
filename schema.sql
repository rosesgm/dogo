-- ============================================================
-- SCHEMA: dogodb
-- ============================================================

CREATE DATABASE IF NOT EXISTS dogodb;
USE dogodb;

CREATE TABLE user (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    name     VARCHAR(100) NOT NULL,
    email    VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    profile  TINYINT NOT NULL DEFAULT 2,   -- 1=ADMIN, 2=CUSTOMER
    is_active BIT(1) NOT NULL DEFAULT 1
);
-- nomas haz un alter table para agregar una columna balance a la tabla de account
CREATE TABLE account (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    number        VARCHAR(20) NOT NULL UNIQUE,
    creation_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    balance       DECIMAL(12,2) NOT NULL DEFAULT 0.00,   -- NUEVO: saldo actualizado por trigger
    id_user       INT NOT NULL,
    FOREIGN KEY (id_user) REFERENCES user(id)
);

CREATE TABLE transaction (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    description VARCHAR(255),
    date        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    amount      DECIMAL(12,2) NOT NULL,
    type        TINYINT NOT NULL,           -- 1=INCOME, 2=EXPENSE
    id_account  INT NOT NULL,
    FOREIGN KEY (id_account) REFERENCES account(id)
);

CREATE TABLE log (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    date        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    description VARCHAR(255),
    type        TINYINT NOT NULL,           -- 1=LOGIN,2=SAVE,3=EDIT,4=DELETE
    id_user     INT NOT NULL,
    FOREIGN KEY (id_user) REFERENCES user(id)
);

CREATE TABLE permission (
    id      INT AUTO_INCREMENT PRIMARY KEY,
    id_user INT NOT NULL,
    value   TINYINT NOT NULL,
    FOREIGN KEY (id_user) REFERENCES user(id)
);

-- ============================================================
-- VIEW: resumen de cuenta por usuario
-- Usa: JOIN, columnas calculadas
--Usada en :Account.get_summary()
-- ============================================================
CREATE VIEW v_account_summary AS
    SELECT
        u.id        AS user_id,
        u.name      AS user_name,
        u.email,
        a.id        AS account_id,
        a.number    AS account_number,
        a.balance,
        a.creation_date,
        COUNT(t.id) AS total_transactions
    FROM user u
    INNER JOIN account a ON a.id_user = u.id
    LEFT JOIN  transaction t ON t.id_account = a.id
    GROUP BY u.id, u.name, u.email, a.id, a.number, a.balance, a.creation_date;

-- ============================================================
-- TRIGGER: al insertar una transacción, actualiza el saldo
-- Se dispara en la app cuando se hace depósito o retiro
-- Usada en: Transaction.save()
-- ============================================================
DELIMITER $$
CREATE TRIGGER trg_update_balance
AFTER INSERT ON transaction
FOR EACH ROW
BEGIN
    IF NEW.type = 1 THEN          -- INCOME: suma
        UPDATE account SET balance = balance + NEW.amount WHERE id = NEW.id_account;
    ELSEIF NEW.type = 2 THEN      -- EXPENSE: resta
        UPDATE account SET balance = balance - NEW.amount WHERE id = NEW.id_account;
    END IF;
END$$
DELIMITER ;