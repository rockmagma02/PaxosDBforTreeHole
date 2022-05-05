USE TreeHole;

CREATE TABLE `Account` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `mail` char(128) NOT NULL,
  `passwordHash` char(128) NOT NULL,
  `createDatetime` datetime NOT NULL
) ENGINE='InnoDB';