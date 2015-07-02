-- phpMyAdmin SQL Dump
-- version 3.4.9
-- http://www.phpmyadmin.net
--
-- Machine: localhost
-- Genereertijd: 02 jul 2015 om 21:59
-- Serverversie: 5.5.20
-- PHP-Versie: 5.4.40

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `skybrarydev`
--

-- --------------------------------------------------------

--
-- Tabelstructuur voor tabel `demo_recommendations`
--

CREATE TABLE IF NOT EXISTS `demo_recommendations` (
  `rec_id` int(11) NOT NULL AUTO_INCREMENT,
  `page_id_X` int(11) NOT NULL,
  `page_id_Y` int(11) NOT NULL,
  `score` float(10,2) NOT NULL,
  `algorithm` varchar(32) COLLATE latin1_general_ci NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`rec_id`),
  UNIQUE KEY `unique_key` (`page_id_X`,`page_id_Y`,`algorithm`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_general_ci AUTO_INCREMENT=1 ;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
