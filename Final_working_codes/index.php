<!-- <?php

// HubSpot API Endpoint
define("HUBSPOT_API_URL", "https://api.hubapi.com/crm/v3/objects/companies");
define("MERGE_API_URL", "https://api.hubapi.com/crm/v3/objects/companies/merge");

// HubSpot Access Token (replace with your actual token)
define("ACCESS_TOKEN", "pat-na1-b1d4ba68-8d61-4618-ae01-6601edaa3064");

// Headers for Authentication
$HEADERS = [
    "Authorization: Bearer " . ACCESS_TOKEN,
    "Content-Type: application/json"
];

function fetch_companies()
{
    global $HEADERS;
    $after = null;
    $all_companies = [];

    do {
        $params = [
            "limit" => 100,
            "properties" => ["name", "phone", "domain"]
        ];

        if ($after) {
            $params["after"] = $after;
        }

        $url = HUBSPOT_API_URL . "?" . http_build_query($params);
        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, $HEADERS);
        $response = curl_exec($ch);
        curl_close($ch);

        $data = json_decode($response, true);

        if (isset($data["results"])) {
            foreach ($data["results"] as $company) {
                $all_companies[] = [
                    "id" => $company["id"],
                    "name" => $company["properties"]["name"] ?? "",
                    "phone" => $company["properties"]["phone"] ?? "",
                    "domain" => $company["properties"]["domain"] ?? ""
                ];
            }

            $after = $data["paging"]["next"]["after"] ?? null;
        } else {
            echo "Error fetching companies: " . json_encode($data) . "\n";
            break;
        }
    } while ($after);

    return $all_companies;
}

function find_duplicates($companies)
{
    $grouped = [];

    // Group by (name, phone)
    foreach ($companies as $company) {
        $key = $company["name"] . "|" . $company["phone"];
        $grouped[$key][] = $company;
    }

    $duplicate_companies = [];

    foreach ($grouped as $key => $group) {
        if (count($group) > 1) {
            $unique_domains = array_unique(array_column($group, "domain"));

            if (count($unique_domains) > 1) {
                $duplicate_companies[] = [
                    "name" => explode("|", $key)[0],
                    "phone" => explode("|", $key)[1],
                    "company_ids" => implode(" & ", array_column($group, "id")),
                    "domains" => implode(" | ", $unique_domains)
                ];
            }
        }
    }

    return $duplicate_companies;
}

function merge_duplicate_companies($duplicate_companies)
{
    global $HEADERS;

    foreach ($duplicate_companies as $duplicate) {
        $company_ids = explode(" & ", $duplicate["company_ids"]);

        if (count($company_ids) > 1) {
            $primary_id = $company_ids[0];

            for ($i = 1; $i < count($company_ids); $i++) {
                $merge_payload = json_encode([
                    "primaryObjectId" => $primary_id,
                    "objectIdToMerge" => $company_ids[$i]
                ]);

                $ch = curl_init(MERGE_API_URL);
                curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
                curl_setopt($ch, CURLOPT_HTTPHEADER, $HEADERS);
                curl_setopt($ch, CURLOPT_POST, true);
                curl_setopt($ch, CURLOPT_POSTFIELDS, $merge_payload);
                $response = curl_exec($ch);
                curl_close($ch);

                if ($response) {
                    // Handle success case
                } else {
                    // Handle failure case
                }
            }
        }
    }
}

// Run the script
$all_companies = fetch_companies();
$duplicate_companies = find_duplicates($all_companies);
merge_duplicate_companies($duplicate_companies);

?> -->
