USE TreeHole;


CREATE USER 'TreeHoleRead'@'%' IDENTIFIED BY 'read';
GRANT SELECT ON `TreeHole`.* TO 'TreeHoleRead'@'%';

CREATE USER 'TreeHoleWrite'@'%' IDENTIFIED BY 'write';
GRANT ALTER, CREATE, CREATE VIEW, DELETE, INDEX, INSERT, REFERENCES, SELECT, SHOW VIEW, TRIGGER, UPDATE, ALTER ROUTINE, EXECUTE ON `TreeHole`.* TO 'TreeHoleWrite'@'%';

CREATE TABLE `Account` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `mail` char(128) NOT NULL,
  `passwordHash` char(128) NOT NULL,
  `createDatetime` datetime NOT NULL
) ENGINE='InnoDB';

CREATE TABLE `HoleContent` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `treeId` bigint unsigned NOT NULL,
  `content` text NOT NULL,
  `auhor` char(128) NOT NULL,
  `createTime` datetime NOT NULL
) ENGINE='InnoDB';

CREATE TABLE `instructionBackup` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `pointTable` char(128) NOT NULL,
  `pointID` bigint NOT NULL
) ENGINE='InnoDB';

CREATE TABLE `PaxosTurns` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `status` char(128) NOT NULL
) ENGINE='InnoDB';