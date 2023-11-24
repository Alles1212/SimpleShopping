-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- 主機： 127.0.0.1
-- 產生時間： 2023-11-23 06:05:52
-- 伺服器版本： 10.4.28-MariaDB
-- PHP 版本： 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 資料庫： `test`
--

-- --------------------------------------------------------

--
-- 資料表結構 `customer_cart`
--

CREATE TABLE `customer_cart` (
  `id` int(11) NOT NULL,
  `product` text NOT NULL,
  `price` int(11) NOT NULL,
  `amount` int(11) NOT NULL,
  `sumPrice` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- 傾印資料表的資料 `customer_cart`
--

INSERT INTO `customer_cart` (`id`, `product`, `price`, `amount`, `sumPrice`) VALUES
(4, 'banana', 10, 10, 100),
(8, 'Watermelon', 71, 12, 852);

-- --------------------------------------------------------

--
-- 資料表結構 `product`
--

CREATE TABLE `product` (
  `id` int(11) NOT NULL,
  `name` varchar(15) NOT NULL,
  `price` int(11) NOT NULL,
  `stock` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- 傾印資料表的資料 `product`
--

INSERT INTO `product` (`id`, `name`, `price`, `stock`) VALUES
(1, 'banana', 10, 10),
(2, 'apple', 50, 6),
(3, 'Watermelon', 71, 12);

-- --------------------------------------------------------

--
-- 資料表結構 `shop_cart`
--

CREATE TABLE `shop_cart` (
  `id` int(11) NOT NULL,
  `p_id` int(5) NOT NULL,
  `amount` int(5) NOT NULL,
  `paid` int(5) NOT NULL DEFAULT 0,
  `delivered` int(5) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- 資料表結構 `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `name` text NOT NULL,
  `password` text NOT NULL,
  `pos` int(5) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- 傾印資料表的資料 `users`
--

INSERT INTO `users` (`id`, `name`, `password`, `pos`) VALUES
(0, 'Alles', '1212', 0),
(0, 'shop', '1', 1);

--
-- 已傾印資料表的索引
--

--
-- 資料表索引 `customer_cart`
--
ALTER TABLE `customer_cart`
  ADD PRIMARY KEY (`id`);

--
-- 資料表索引 `product`
--
ALTER TABLE `product`
  ADD PRIMARY KEY (`id`);

--
-- 資料表索引 `shop_cart`
--
ALTER TABLE `shop_cart`
  ADD PRIMARY KEY (`id`);

--
-- 在傾印的資料表使用自動遞增(AUTO_INCREMENT)
--

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `customer_cart`
--
ALTER TABLE `customer_cart`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `product`
--
ALTER TABLE `product`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `shop_cart`
--
ALTER TABLE `shop_cart`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=26;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;