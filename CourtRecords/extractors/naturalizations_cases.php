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

    // Open MySQL
    connect();
    
    // GET DB DATA
    try {
    
        echo "case_id, case_number, actiontype, year, container, box_number, drawer_number, notes, county, court, call_number <br />";
        
        $result = mysql_query("SELECT n.id, n.date, c.short_name, n.notes, r.short_name AS `actiontype`
                               FROM  naturalizations n, record_types r, collections c
                               WHERE n.record_type_id = r.id AND n.collection_id = c.id");
        while($row = mysql_fetch_assoc($result)) {
            echo $row['id'] . ','; #case id
            echo ','; #casenumber
            echo $row['actiontype'] .','; #actiontype
            echo $row['date'] . ','; #year
            echo ','; #container
            echo ','; #box_number
            echo ','; #drawer_number
            echo $row['notes'] . ','; #county
            echo $row['short_name'] . ','; #county
            echo 'Circuit Court,'; #court
            echo ''; #call_number
            
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