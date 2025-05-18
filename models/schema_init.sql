CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    language VARCHAR(10) NOT NULL,
    content TEXT NOT NULL
);

CREATE TABLE elements (
    id SERIAL PRIMARY KEY,
    article_id INT NOT NULL,
    type VARCHAR(20) NOT NULL,
    path TEXT NOT NULL,
    FOREIGN KEY (article_id) REFERENCES articles(id)
);

CREATE TABLE fragments (
    id SERIAL PRIMARY KEY,
    article_id INT NOT NULL,
    element_id INT NOT NULL,
    content TEXT NOT NULL,
    FOREIGN KEY (article_id) REFERENCES articles(id),
    FOREIGN KEY (element_id) REFERENCES elements(id)
);

CREATE TABLE preprocessing_results (
    id SERIAL PRIMARY KEY,
    fragment_id INT NOT NULL,
    step VARCHAR(50) NOT NULL,
    processed_text TEXT NOT NULL,
    FOREIGN KEY (fragment_id) REFERENCES fragments(id)
);

CREATE TABLE graphs (
    id SERIAL PRIMARY KEY,
    fragment_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    graph_data JSON NOT NULL,
    FOREIGN KEY (fragment_id) REFERENCES fragments(id)
);