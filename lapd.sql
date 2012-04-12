-- phpMyAdmin SQL Dump
-- version 3.4.5deb1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Apr 04, 2012 at 09:56 PM
-- Server version: 5.1.61
-- PHP Version: 5.3.6-13ubuntu3.6

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `lapd`
--

-- --------------------------------------------------------

--
-- Table structure for table `Officers`
--
DROP TABLE `Officers`;
CREATE TABLE IF NOT EXISTS `Officers` (
  `serialNo` int(11) NOT NULL,
  `divisionID` int(2) NOT NULL,
  `rankID` int(11) NOT NULL,
  `lastName` text NOT NULL,
  `firstName` text NOT NULL,
  PRIMARY KEY (`serialNo`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `Officers`
--

INSERT INTO `Officers` (`serialNo`, `divisionID`, `rankID`, `lastName`, `firstName`) VALUES
(69696, 3, 3, 'Ball', 'Ryan'),
(12345, 3, 2, 'Smith', 'John'),
(44444, 3, 1, 'Chiba', 'Ryo'),
(44445, 3, 2, 'Hello', 'Ryo'),
(44446, 3, 3, 'Bob', 'Ryo');

-- --------------------------------------------------------

--
-- Table structure for table `OfficerSchedules`
--
DROP TABLE `OfficerSchedules`;
CREATE TABLE IF NOT EXISTS `OfficerSchedules` (
  `serialNo` int(11) NOT NULL,
  `dpID` int(11) NOT NULL,
  `watchID` tinyint(4) NOT NULL DEFAULT '0',
  `assignmentID` smallint(6) NOT NULL DEFAULT '0',
  `schedule` varchar(55) DEFAULT NULL,
  `request` tinyint(1) NOT NULL DEFAULT '1',
  `genSchedule` varchar(55) DEFAULT NULL,
  PRIMARY KEY (`serialNo`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `OfficerSchedules`
--

INSERT INTO `OfficerSchedules` (`serialNo`, `dpID`, `watchID`, `assignmentID`, `schedule`, `request`, `genSchedule`) VALUES
(12345, 22, 0, 0, 'N N N N V N', 1, 'N N N R'),
(44444, 22, 0, 0, 'N N N V N N', 1, 'R N N N'),
(44445, 22, 0, 0, 'V V N N N V', 1, 'R N N N'),
(44446, 22, 0, 0, 'N V T V N V', 1, 'R N N N'),
(69696, 22, 0, 0, 'N N N N T N', 1, 'N R N N');

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
