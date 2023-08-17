-- MySQL dump 10.13  Distrib 5.7.39, for Win64 (x86_64)
--
-- Host: localhost    Database: labyrinth
-- ------------------------------------------------------
-- Server version	5.7.39-log

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
-- Table structure for table `maze_scores`
--

DROP TABLE IF EXISTS `maze_scores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `maze_scores` (
  `gamerid` char(4) NOT NULL,
  `highscore` int(11) DEFAULT NULL,
  `lastscore` int(11) DEFAULT NULL,
  `lastplayed` date DEFAULT NULL,
  `timesplayed` int(11) DEFAULT NULL,
  PRIMARY KEY (`gamerid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `maze_scores`
--

LOCK TABLES `maze_scores` WRITE;
/*!40000 ALTER TABLE `maze_scores` DISABLE KEYS */;
INSERT INTO `maze_scores` VALUES ('3CD5',3596,3156,'2022-11-24',7),('4DE6',3045,3045,'2022-11-28',2),('QU60',2954,2531,'2022-11-30',3);
/*!40000 ALTER TABLE `maze_scores` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `player_details`
--

DROP TABLE IF EXISTS `player_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `player_details` (
  `gamerid` char(4) NOT NULL,
  `username` varchar(32) NOT NULL,
  `email` varchar(32) NOT NULL,
  `password` varchar(32) NOT NULL,
  PRIMARY KEY (`gamerid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `player_details`
--

LOCK TABLES `player_details` WRITE;
/*!40000 ALTER TABLE `player_details` DISABLE KEYS */;
INSERT INTO `player_details` VALUES ('2BC4','DEF_456','def@gmail.com','RkVEXzY1NA=='),('QU60','ABC_123','testuser1@gmail.com','Q2JhXzMyMQ==');
/*!40000 ALTER TABLE `player_details` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pong_scores`
--

DROP TABLE IF EXISTS `pong_scores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pong_scores` (
  `gamerid` char(4) NOT NULL,
  `highscore` int(11) DEFAULT NULL,
  `lastscore` int(11) DEFAULT NULL,
  `lastplayed` date DEFAULT NULL,
  `timesplayed` int(11) DEFAULT NULL,
  PRIMARY KEY (`gamerid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pong_scores`
--

LOCK TABLES `pong_scores` WRITE;
/*!40000 ALTER TABLE `pong_scores` DISABLE KEYS */;
INSERT INTO `pong_scores` VALUES ('1AB3',13,10,'2022-11-26',3),('2BC4',110,60,'2022-11-12',23),('4DE6',70,70,'2022-11-21',12),('QU60',30,20,'2022-11-30',2);
/*!40000 ALTER TABLE `pong_scores` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `snake_scores`
--

DROP TABLE IF EXISTS `snake_scores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `snake_scores` (
  `gamerid` char(4) NOT NULL,
  `highscore` int(11) DEFAULT NULL,
  `lastscore` int(11) DEFAULT NULL,
  `lastplayed` date DEFAULT NULL,
  `timesplayed` int(11) DEFAULT NULL,
  PRIMARY KEY (`gamerid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `snake_scores`
--

LOCK TABLES `snake_scores` WRITE;
/*!40000 ALTER TABLE `snake_scores` DISABLE KEYS */;
INSERT INTO `snake_scores` VALUES ('1AB3',2,2,'2022-11-26',1),('4DE6',3,2,'2022-11-23',2),('QU60',6,6,'2022-11-01',7);
/*!40000 ALTER TABLE `snake_scores` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wordle_scores`
--

DROP TABLE IF EXISTS `wordle_scores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wordle_scores` (
  `gamerid` char(4) NOT NULL,
  `highscore` int(11) DEFAULT NULL,
  `lastscore` int(11) DEFAULT NULL,
  `lastplayed` date DEFAULT NULL,
  `timesplayed` int(11) DEFAULT NULL,
  PRIMARY KEY (`gamerid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wordle_scores`
--

LOCK TABLES `wordle_scores` WRITE;
/*!40000 ALTER TABLE `wordle_scores` DISABLE KEYS */;
INSERT INTO `wordle_scores` VALUES ('1AB3',50,50,'2022-11-28',1),('3CD5',30,30,'2022-11-21',6),('4DE6',40,50,'2022-11-24',12);
/*!40000 ALTER TABLE `wordle_scores` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-12-01  7:17:50
