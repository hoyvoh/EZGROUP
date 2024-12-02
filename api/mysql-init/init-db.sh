#!/bin/sh

# Create database and user
echo "CREATE DATABASE IF NOT EXISTS ${MYSQL_DATABASE};" > /docker-entrypoint-initdb.d/1-init.sql
echo "CREATE USER IF NOT EXISTS '${MYSQL_USER}'@'%' IDENTIFIED BY '${MYSQL_PASSWORD}';" >> /docker-entrypoint-initdb.d/1-init.sql
echo "GRANT ALL PRIVILEGES ON ${MYSQL_DATABASE}.* TO '${MYSQL_USER}'@'%';" >> /docker-entrypoint-initdb.d/1-init.sql
echo "FLUSH PRIVILEGES;" >> /docker-entrypoint-initdb.d/1-init.sql

# Add stored procedure
cat <<EOF >> /docker-entrypoint-initdb.d/1-init.sql

DELIMITER $$

-- Stored procedure to delete a blog post and its related data
CREATE PROCEDURE delete_blog_post(IN post_id INT)
BEGIN
    -- Delete related comments
    DELETE FROM blog_comment WHERE post_id = post_id;

    -- Delete related images
    DELETE FROM blog_image WHERE post_id = post_id;

    -- Delete related likes
    DELETE FROM blog_like WHERE post_id = post_id;

    -- Finally, delete the post
    DELETE FROM blog_post WHERE id = post_id;
END$$

DELIMITER ;

EOF

# Add trigger (optional)
cat <<EOF >> /docker-entrypoint-initdb.d/1-init.sql

DELIMITER $$

-- Trigger to handle related data deletion before a blog post is deleted
CREATE TRIGGER before_blog_post_delete
BEFORE DELETE ON blog_post
FOR EACH ROW
BEGIN
    DELETE FROM blog_comment WHERE post_id = OLD.id;
    DELETE FROM blog_image WHERE post_id = OLD.id;
    DELETE FROM blog_like WHERE post_id = OLD.id;
END$$

DELIMITER ;

EOF

# Output the complete initialization script for debugging purposes
cat /docker-entrypoint-initdb.d/1-init.sql
