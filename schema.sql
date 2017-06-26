-- MySQL dump 10.13  Distrib 5.7.17, for Linux (x86_64)
--
-- Host: groan    Database: tor
-- ------------------------------------------------------
-- Server version	5.7.17

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `bitcoin_address`
--

DROP TABLE IF EXISTS `bitcoin_address`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bitcoin_address` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `address` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `address` (`address`)
) ENGINE=InnoDB AUTO_INCREMENT=53732 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `bitcoin_address_link`
--

DROP TABLE IF EXISTS `bitcoin_address_link`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bitcoin_address_link` (
  `page` int(11) NOT NULL DEFAULT '0',
  `bitcoin_address` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`page`,`bitcoin_address`),
  KEY `idx_bitcoin_address_link` (`page`),
  KEY `fk_bitcoin_address_link__bitcoin_address` (`bitcoin_address`),
  CONSTRAINT `fk_bitcoin_address_link__bitcoin_address` FOREIGN KEY (`bitcoin_address`) REFERENCES `bitcoin_address` (`id`),
  CONSTRAINT `fk_bitcoin_address_link__page` FOREIGN KEY (`page`) REFERENCES `page` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `category`
--

DROP TABLE IF EXISTS `category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `category` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  `is_auto` tinyint(1) DEFAULT '1',
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `category_link`
--

DROP TABLE IF EXISTS `category_link`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `category_link` (
  `domain` int(11) NOT NULL,
  `category` int(11) NOT NULL,
  `is_confirmed` tinyint(1) DEFAULT '0',
  `is_valid` tinyint(1) DEFAULT '1',
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`domain`,`category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `categorylink`
--

DROP TABLE IF EXISTS `categorylink`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `categorylink` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `domain` int(11) NOT NULL,
  `category` int(11) NOT NULL,
  `is_valid` tinyint(1) NOT NULL,
  `is_confirmed` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_categorylink__category` (`category`),
  KEY `idx_categorylink__domain` (`domain`),
  CONSTRAINT `fk_categorylink__category` FOREIGN KEY (`category`) REFERENCES `category` (`id`),
  CONSTRAINT `fk_categorylink__domain` FOREIGN KEY (`domain`) REFERENCES `domain` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=210 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `clone_group`
--

DROP TABLE IF EXISTS `clone_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `clone_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=30138 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `daily_stat`
--

DROP TABLE IF EXISTS `daily_stat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `daily_stat` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_at` datetime DEFAULT NULL,
  `unique_visitors` int(11) DEFAULT NULL,
  `total_onions` int(11) DEFAULT NULL,
  `new_onions` int(11) DEFAULT NULL,
  `total_clones` int(11) DEFAULT NULL,
  `total_onions_all` int(11) DEFAULT NULL,
  `new_onions_all` int(11) DEFAULT NULL,
  `banned` int(11) DEFAULT NULL,
  `up_right_now` int(11) DEFAULT NULL,
  `up_right_now_all` int(11) DEFAULT NULL,
  `banned_up_last_24` int(11) DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `idx_daily_stat_created_at` (`created_at`)
) ENGINE=InnoDB AUTO_INCREMENT=126 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `domain`
--

DROP TABLE IF EXISTS `domain`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `domain` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `host` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `port` int(11) NOT NULL,
  `ssl` tinyint(1) NOT NULL,
  `is_up` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL,
  `visited_at` datetime NOT NULL,
  `title` mediumtext COLLATE utf8_unicode_ci,
  `last_alive` datetime DEFAULT NULL,
  `is_crap` tinyint(1) DEFAULT '0',
  `is_genuine` tinyint(1) DEFAULT '0',
  `is_fake` tinyint(1) DEFAULT '0',
  `ssh_fingerprint` int(11) DEFAULT NULL,
  `is_subdomain` tinyint(1) DEFAULT '0',
  `server` varchar(255) COLLATE utf8_unicode_ci DEFAULT '',
  `powered_by` varchar(255) COLLATE utf8_unicode_ci DEFAULT '',
  `dead_in_a_row` int(11) DEFAULT '0',
  `next_scheduled_check` datetime DEFAULT CURRENT_TIMESTAMP,
  `is_banned` tinyint(1) DEFAULT '0',
  `portscanned_at` datetime DEFAULT '1969-12-31 19:00:00',
  `path_scanned_at` datetime DEFAULT '1969-12-31 19:00:00',
  `useful_404_scanned_at` datetime DEFAULT '1969-12-31 19:00:00',
  `useful_404` tinyint(1) DEFAULT '0',
  `useful_404_php` tinyint(1) DEFAULT '0',
  `useful_404_dir` tinyint(1) DEFAULT '0',
  `clone_group` int(11) DEFAULT NULL,
  `new_clone_group` int(11) DEFAULT NULL,
  `ban_exempt` tinyint(1) DEFAULT '0',
  `manual_genuine` tinyint(1) DEFAULT '0',
  `language` varchar(2) COLLATE utf8_unicode_ci DEFAULT '',
  `description_json` varchar(10240) COLLATE utf8_unicode_ci DEFAULT NULL,
  `description_json_at` datetime DEFAULT '1969-12-31 19:00:00',
  `whatweb_at` datetime DEFAULT '1969-12-31 19:00:00',
  PRIMARY KEY (`id`),
  KEY `created_at_idx` (`created_at`),
  KEY `last_alive_idx` (`last_alive`),
  KEY `host_idx` (`host`),
  KEY `idx_domain__ssh_fingerprint` (`ssh_fingerprint`),
  KEY `idx_domain__clone_group` (`clone_group`),
  KEY `idx_domain__new_clone_group` (`new_clone_group`),
  KEY `language_idx` (`language`),
  KEY `idx_domain_title` (`title`(255)),
  CONSTRAINT `fk_domain__clone_group` FOREIGN KEY (`clone_group`) REFERENCES `clone_group` (`id`),
  CONSTRAINT `fk_domain__new_clone_group` FOREIGN KEY (`new_clone_group`) REFERENCES `clone_group` (`id`),
  CONSTRAINT `fk_domain__ssh_fingerprint` FOREIGN KEY (`ssh_fingerprint`) REFERENCES `ssh_fingerprint` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=298011 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `email`
--

DROP TABLE IF EXISTS `email`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `email` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `address` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `address` (`address`)
) ENGINE=InnoDB AUTO_INCREMENT=115630 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `email_link`
--

DROP TABLE IF EXISTS `email_link`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `email_link` (
  `email` int(11) NOT NULL DEFAULT '0',
  `page` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`page`,`email`),
  KEY `idx_email_link` (`page`),
  KEY `fk_email_link__email` (`email`),
  CONSTRAINT `fk_email_link__email` FOREIGN KEY (`email`) REFERENCES `email` (`id`),
  CONSTRAINT `fk_email_link__page` FOREIGN KEY (`page`) REFERENCES `page` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `headless_bot`
--

DROP TABLE IF EXISTS `headless_bot`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `headless_bot` (
  `uuid` varchar(36) COLLATE utf8_unicode_ci NOT NULL,
  `kind` varchar(128) COLLATE utf8_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`uuid`),
  KEY `kind_idx` (`kind`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `headlessbot`
--

DROP TABLE IF EXISTS `headlessbot`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `headlessbot` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uuid` varchar(36) NOT NULL,
  `kind` varchar(128) NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `open_port`
--

DROP TABLE IF EXISTS `open_port`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `open_port` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `port` int(11) NOT NULL,
  `domain` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_open_port__domain` (`domain`),
  CONSTRAINT `fk_open_port__domain` FOREIGN KEY (`domain`) REFERENCES `domain` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=31846 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `page`
--

DROP TABLE IF EXISTS `page`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `page` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `url` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `title` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `code` int(11) NOT NULL,
  `domain` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `visited_at` datetime NOT NULL,
  `is_frontpage` tinyint(1) DEFAULT '0',
  `size` int(11) DEFAULT '0',
  `path` varchar(1024) COLLATE utf8_unicode_ci DEFAULT '',
  PRIMARY KEY (`id`),
  UNIQUE KEY `url` (`url`),
  KEY `idx_page__domain` (`domain`),
  KEY `page_path_idx` (`path`(255)),
  CONSTRAINT `fk_page__domain` FOREIGN KEY (`domain`) REFERENCES `domain` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13358229 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `page_link`
--

DROP TABLE IF EXISTS `page_link`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `page_link` (
  `link_from` int(11) NOT NULL DEFAULT '0',
  `link_to` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`link_from`,`link_to`),
  KEY `idx_page_link` (`link_to`),
  CONSTRAINT `fk_page_link__link_from` FOREIGN KEY (`link_from`) REFERENCES `page` (`id`),
  CONSTRAINT `fk_page_link__link_to` FOREIGN KEY (`link_to`) REFERENCES `page` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `request_log`
--

DROP TABLE IF EXISTS `request_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `request_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uuid` varchar(36) COLLATE utf8_unicode_ci DEFAULT '',
  `uuid_is_fresh` tinyint(1) DEFAULT '1',
  `created_at` datetime DEFAULT NULL,
  `agent` varchar(256) COLLATE utf8_unicode_ci DEFAULT NULL,
  `path` varchar(1024) COLLATE utf8_unicode_ci DEFAULT NULL,
  `full_path` varchar(1024) COLLATE utf8_unicode_ci DEFAULT NULL,
  `referrer` varchar(1024) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_reqlog_created_at` (`created_at`)
) ENGINE=InnoDB AUTO_INCREMENT=6902384 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `search_log`
--

DROP TABLE IF EXISTS `search_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `search_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `request_log` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `has_searchterms` tinyint(1) DEFAULT '0',
  `searchterms` varchar(256) COLLATE utf8_unicode_ci DEFAULT NULL,
  `has_raw_searchterms` tinyint(1) DEFAULT '0',
  `raw_searchterms` varchar(256) COLLATE utf8_unicode_ci DEFAULT NULL,
  `is_firstpage` tinyint(1) DEFAULT '0',
  `is_json` tinyint(1) DEFAULT '0',
  `context` varchar(1024) COLLATE utf8_unicode_ci DEFAULT NULL,
  `results` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_searchlog_created_at` (`created_at`),
  KEY `idx_search_log__request_log` (`request_log`),
  CONSTRAINT `fk_search_log__request_log` FOREIGN KEY (`request_log`) REFERENCES `request_log` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=699313 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ssh_fingerprint`
--

DROP TABLE IF EXISTS `ssh_fingerprint`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ssh_fingerprint` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fingerprint` varchar(450) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `fingerprint` (`fingerprint`)
) ENGINE=InnoDB AUTO_INCREMENT=154 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `web_component`
--

DROP TABLE IF EXISTS `web_component`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `web_component` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) COLLATE utf8_unicode_ci DEFAULT NULL,
  `version` varchar(128) COLLATE utf8_unicode_ci DEFAULT NULL,
  `account` varchar(128) COLLATE utf8_unicode_ci DEFAULT NULL,
  `string` varchar(512) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_web_component_name` (`name`),
  KEY `idx_web_component_version` (`version`),
  KEY `idx_web_component_account` (`account`),
  KEY `idx_web_component_string` (`string`),
  KEY `idx_web_component_name_version` (`name`,`version`),
  KEY `idx_web_component_name_account` (`name`,`account`),
  KEY `idx_web_component_name_string` (`name`,`string`)
) ENGINE=InnoDB AUTO_INCREMENT=1352 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `web_component_link`
--

DROP TABLE IF EXISTS `web_component_link`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `web_component_link` (
  `web_component` int(11) NOT NULL DEFAULT '0',
  `domain` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`web_component`,`domain`),
  KEY `idx_component_link_web` (`web_component`),
  KEY `idx_component_link_domain` (`domain`),
  KEY `idx_web_component_link` (`web_component`),
  CONSTRAINT `fk_web_component_link__domain` FOREIGN KEY (`domain`) REFERENCES `domain` (`id`),
  CONSTRAINT `fk_web_component_link__web_component` FOREIGN KEY (`web_component`) REFERENCES `web_component` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-06-26 11:34:59
