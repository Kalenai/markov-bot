CREATE TABLE transition (
    first_word VARCHAR,
    second_word VARCHAR,
    result_word VARCHAR,
    frequency INTEGER,
    beginning BOOLEAN,
    PRIMARY KEY(first_word, second_word, result_word)
);