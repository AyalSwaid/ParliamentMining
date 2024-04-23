-- ###################################  debates  ###################################
CREATE TABLE topics(
    topic_id INT AUTO_INCREMENT PRIMARY KEY,
    topic VARCHAR(50)
);


CREATE TABLE countries(
    country_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50)
);


CREATE TABLE parties(
    party_id INT AUTO_INCREMENT PRIMARY KEY,
    party VARCHAR(50),
    country INT,

    FOREIGN KEY (country) REFERENCES countries(country_id) ON DELETE SET NULL
);


CREATE TABLE bills(
    bill_id INT AUTO_INCREMENT PRIMARY KEY,
    title INT,
    bill_date DATE
);


CREATE TABLE debates
(
  debate_id INT AUTO_INCREMENT PRIMARY KEY,
  topic INT,
  title VARCHAR(50),
  summary VARCHAR(2000),
  content_file_path VARCHAR(100),
  debate_date DATE,
  is_issue BOOLEAN,
  country INT,

  FOREIGN KEY (topic) REFERENCES topics(topic_id) ON DELETE SET NULL,
  FOREIGN KEY (country) REFERENCES countries(country_id) ON DELETE SET NULL
);


CREATE TABLE members(
    member_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    party INT,
    house VARCHAR(50),
    startDate DATE,
    endDate DATE,

    FOREIGN KEY (party) REFERENCES parties(party_id) ON DELETE SET NULL,

);


CREATE TABLE debates_members(
    debate_id INT,
    member_id INT,
    is_sponsor BOOLEAN,

    FOREIGN KEY (debate_id) REFERENCES debates(debate_id) ON DELETE CASCADE
);

