-- 
-- depends: 
CREATE TABLE users (
        id SERIAL NOT NULL,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL,
        CONSTRAINT pk_users PRIMARY KEY (id),
        CONSTRAINT uq_users_email UNIQUE (email)
);
CREATE TABLE groups (
        id SERIAL NOT NULL,
        name VARCHAR(255) NOT NULL,
        CONSTRAINT pk_groups PRIMARY KEY (id)
);
CREATE TABLE memberships (
        user_id INTEGER NOT NULL,
        group_id INTEGER NOT NULL,
        CONSTRAINT pk_memberships PRIMARY KEY (user_id, group_id),
        CONSTRAINT fk_memberships_user_id_users FOREIGN KEY(user_id) REFERENCES users (id),
        CONSTRAINT fk_memberships_group_id_groups FOREIGN KEY(group_id) REFERENCES groups (id)
);
CREATE TABLE bills (
        id SERIAL NOT NULL,
        description VARCHAR(255) NOT NULL,
        total_amount FLOAT NOT NULL,
        payer_id INTEGER NOT NULL,
        group_id INTEGER NOT NULL,
        CONSTRAINT pk_bills PRIMARY KEY (id),
        CONSTRAINT fk_bills_payer_id_users FOREIGN KEY(payer_id) REFERENCES users (id),
        CONSTRAINT fk_bills_group_id_groups FOREIGN KEY(group_id) REFERENCES groups (id)
);
CREATE TABLE bill_shares (
        bill_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        amount FLOAT NOT NULL,
        CONSTRAINT pk_bill_participants PRIMARY KEY (bill_id, user_id),
        CONSTRAINT fk_bill_participants_bill_id_bills FOREIGN KEY(bill_id) REFERENCES bills (id),
        CONSTRAINT fk_bill_participants_user_id_users FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE TABLE transactions (
        id SERIAL NOT NULL,
        description VARCHAR(255),
        amount FLOAT NOT NULL,
        payer_id INTEGER NOT NULL,
        bill_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        CONSTRAINT pk_transactions PRIMARY KEY (id),
        CONSTRAINT fk_transactions_payer_id_users FOREIGN KEY(payer_id) REFERENCES users (id),
        CONSTRAINT fk_transactions_bill_id_bills FOREIGN KEY(bill_id) REFERENCES bills (id),
        CONSTRAINT fk_transactions_receiver_id_users FOREIGN KEY(receiver_id) REFERENCES users (id)
)
