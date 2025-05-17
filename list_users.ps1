# Get all users
$allUsers = (Invoke-RestMethod -Uri "http://localhost:8000/users").data.users

Write-Host "Users with tags:"
Write-Host "---------------"

# Check each user for tags
foreach ($user in $allUsers) {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/users/$user/tags"

    if ($response.data.tags.Count -gt 0) {
        # Display user ID and their tags
        Write-Host "$user - Tags: $($response.data.tags -join ', ')"
    }
}

Write-Host ""
Write-Host "Users without tags:"
Write-Host "---------------"

# Check each user again to find users without tags
foreach ($user in $allUsers) {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/users/$user/tags"

    if ($response.data.tags.Count -eq 0) {
        Write-Host "$user"
    }
}

# Show statistics
Write-Host ""
Write-Host "Statistics:"
$withTags = 0
$withoutTags = 0

foreach ($user in $allUsers) {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/users/$user/tags"
    if ($response.data.tags.Count -gt 0) {
        $withTags++
    } else {
        $withoutTags++
    }
}

Write-Host "Total users: $($allUsers.Count)"
Write-Host "Users with tags: $withTags"
Write-Host "Users without tags: $withoutTags"