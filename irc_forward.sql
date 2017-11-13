SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

CREATE DATABASE IF NOT EXISTS `irc_forward` DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;
USE `irc_forward`;

CREATE TABLE `accounts` (
  `discord_snowflake` bigint(32) NOT NULL,
  `irc_username` varchar(32) NOT NULL,
  `irc_token` varchar(32) NOT NULL,
  `allow_dm` tinyint(1) NOT NULL,
  `always_online` tinyint(1) NOT NULL,
  `is_bot` tinyint(1) NOT NULL,
  `highlights` json NOT NULL,
  `always_highlight` tinyint(1) NOT NULL DEFAULT '0'
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

INSERT INTO `accounts` (`discord_snowflake`, `irc_username`, `irc_token`, `allow_dm`, `always_online`, `is_bot`, `highlights`, `always_highlight`) VALUES
(147630584619991040, 'Sunpy', '-TOKEN-', 1, 1, 0, '["sunpy", "emily"]', 0),
(-1, 'DiscordBot', '-TOKEN-', 1, 1, 1, '[]', 0);

CREATE TABLE `cached_users` (
  `userid` int(11) NOT NULL,
  `username` varchar(32) NOT NULL,
  `username_safe` varchar(32) NOT NULL,
  `avatar` varchar(64) NOT NULL,
  `silenced` int(11) NOT NULL DEFAULT '0'
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

CREATE TABLE `settings` (
  `name` varchar(64) NOT NULL,
  `value_int` int(11) DEFAULT NULL,
  `value_string` varchar(128) NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

INSERT INTO `settings` (`name`, `value_int`, `value_string`) VALUES
('irc_srv_addr', NULL, '-IRC-SERVER-'),
('irc_srv_port', 6667, ''),
('irc_srv_channels', NULL, '#osu,#admin,#lobby'),
('discord_token', NULL, '-DISCORD-TOKEN-'),
('osu_srv_frontend', NULL, '-RIPPLE-SERVER-'),
('discord_main_category', NULL, '-MAIN-CATEGORY-'),
('discord_guild', 123456789000000000, ''),
('discord_ignore_categories', NULL, '-IGNORE-ME-');


ALTER TABLE `accounts`
  ADD UNIQUE KEY `discord_snowflake` (`discord_snowflake`);

ALTER TABLE `cached_users`
  ADD UNIQUE KEY `userid` (`userid`);

ALTER TABLE `settings`
  ADD UNIQUE KEY `name` (`name`);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;