-- apply --
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(20) NOT NULL
);
-- rollback --
drop table aerich;

-- pilgrimore_version 1 -- 
