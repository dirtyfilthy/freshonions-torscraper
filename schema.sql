-- MySQL dump 10.13  Distrib 5.5.54, for debian-linux-gnu (x86_64)
--
-- Host: groan    Database: tor
-- ------------------------------------------------------
-- Server version	5.6.33-0ubuntu0.14.04.1

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
-- Table structure for table `clone_group`
--

DROP TABLE IF EXISTS `clone_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `clone_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=995 DEFAULT CHARSET=latin1;
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
  PRIMARY KEY (`id`),
  KEY `created_at_idx` (`created_at`),
  KEY `last_alive_idx` (`last_alive`),
  KEY `host_idx` (`host`),
  KEY `idx_domain__ssh_fingerprint` (`ssh_fingerprint`),
  KEY `idx_domain__clone_group` (`clone_group`),
  KEY `idx_domain__new_clone_group` (`new_clone_group`),
  CONSTRAINT `fk_domain__clone_group` FOREIGN KEY (`clone_group`) REFERENCES `clone_group` (`id`),
  CONSTRAINT `fk_domain__new_clone_group` FOREIGN KEY (`new_clone_group`) REFERENCES `clone_group` (`id`),
  CONSTRAINT `fk_domain__ssh_fingerprint` FOREIGN KEY (`ssh_fingerprint`) REFERENCES `ssh_fingerprint` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=45565 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
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
) ENGINE=InnoDB AUTO_INCREMENT=5177 DEFAULT CHARSET=latin1;
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
) ENGINE=InnoDB AUTO_INCREMENT=1390497 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
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
) ENGINE=InnoDB AUTO_INCREMENT=115 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-02-24  9:36:09
