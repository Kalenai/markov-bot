CREATE TABLE transition (
    first_word VARCHAR,
    second_word VARCHAR,
    result_word VARCHAR,
    frequency INTEGER,
    PRIMARY KEY(first_word, second_word)
);