<?php
// Connection details for MySQL database
$servername = "localhost";
$username = "your_mysql_username";
$password = "your_mysql_password";
$dbname = "delivery_tracking";

// Generate a unique tracking number
function generateTrackingNumber() {
  // Generate a random number or use any unique identifier logic here
  return strtoupper(substr(md5(uniqid(rand(), true)), 0, 8));
}

// Retrieve POST data
$data = json_decode(file_get_contents('php://input'), true);
$status = $data['status'];
$location = $data['location'];

// Create a new connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
  die("Connection failed: " . $conn->connect_error);
}

// Generate a tracking number
$trackingNumber = generateTrackingNumber();

// Insert the delivery record into the database
$sql = "INSERT INTO deliveries (tracking_number, status, location) VALUES (?, ?, ?)";
$stmt = $conn->prepare($sql);
$stmt->bind_param("sss", $trackingNumber, $status, $location);

$response = array();

if ($stmt->execute()) {
  $response["trackingNumber"] = $trackingNumber;
} else {
  $response["message"] = "Failed to create delivery: " . $stmt->error;
}

$stmt->close();
$conn->close();

// Send JSON response
header('Content-Type: application/json');
echo json_encode($response);
?>
