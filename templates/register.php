<?php

$host = 'localhost'; 
$db = 'your_database'; 
$user = 'your_username'; 
$pass = 'your_password'; 


try {
    $pdo = new PDO("mysql:host=$host;dbname=$db", $user, $pass);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    die("Connection failed: " . $e->getMessage());
}


if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $username = trim($_POST['username']);
    $password = $_POST['password'];
    $confirm_password = $_POST['confirm_password'];
    $email = trim($_POST['email']);
    $phone = trim($_POST['phone']);
    $country = trim($_POST['country']);
    
    
    $errors = [];
    if (empty($username) || empty($password) || empty($confirm_password) || empty($email) || empty($phone) || empty($country)) {
        $errors[] = "All fields are required.";
    }
    
    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        $errors[] = "Invalid email format.";
    }
    
    if ($password !== $confirm_password) {
        $errors[] = "Passwords do not match.";
    }
    
    
    if (empty($errors)) {
        
        $hashed_password = password_hash($password, PASSWORD_DEFAULT);
        
        
        $stmt = $pdo->prepare("INSERT INTO users (username, password, email, phone, country) VALUES (:username, :password, :email, :phone, :country)");
        
        
        $stmt->bindParam(':username', $username);
        $stmt->bindParam(':password', $hashed_password);
        $stmt->bindParam(':email', $email);
        $stmt->bindParam(':phone', $phone);
        $stmt->bindParam(':country', $country);
        
        
        if ($stmt->execute()) {
            
            header("Location: /login");
            exit();
        } else {
            echo "Registration failed. Please try again.";
        }
    } else {
        
        foreach ($errors as $error) {
            echo "<p style='color: red;'>$error</p>";
        }
    }
}
?>
