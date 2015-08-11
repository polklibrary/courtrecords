<?php

$conn = null;

function connect() {
    global $conn;
    try {
        $conn = mysql_connect("polk.uwosh.edu","naturalizations","SmBCt7ix");
        if (!$conn) die('Connection Error');
        mysql_select_db("oshpolk_naturalizations", $conn);
    }
    catch (Exception $e) {
        echo "CONN ERROR";
    }
}

function disconnect() {
    global $conn;
    if ($conn != null)
        mysql_close($conn);
}


function wsQuery() {

    $data = '';
    
    // Open MySQL
    connect();
    
    // GET DB DATA
    try {
    
        echo "case_id, entity, prefix, lastname, firstname, middlename, suffix, alternatename, role <br />";
        
        $result = mysql_query("SELECT n.id, n.last_name, n.first_name, n.middle_name, n.alternate_name, r.name
                               FROM  naturalizations n, record_types r, collections c
                               WHERE n.record_type_id = r.id AND n.collection_id = c.id");
        while($row = mysql_fetch_assoc($result)) {
            echo $row['id'] . ','; #case id
            echo $row['last_name']  . ','; #entity
            echo ','; #prefix
            echo $row['last_name']  . ','; #lastname
            echo $row['first_name']  . ','; #firstname
            echo $row['middle_name']  . ','; #middlename
            echo ','; #suffix
            echo $row['alternate_name']  . ','; #alternatename
            echo 'Immigrant'; #role
            
            echo '<br />';
            
            
            
            
        }
    }
    catch (Exception $e) {
        echo "GET Error";
    }
    
    // Close MySQL
    disconnect();
        
}



// init
wsQuery();

?>



