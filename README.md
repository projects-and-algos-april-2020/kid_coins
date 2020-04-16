# Project: Kid Coins
## descritpion: app where kids within a household earn "kid coins" from their parents by doing chores, homework, and extra work. Kid can then exchange coins for pre determined cash amount or free play time or tv time.

### backlog
    * everybody logs in as a user
    * parents become admins
    * admin creates a home/household where their family are the only members
    * each home has a home name and password attached
    * kids and other admins can join created home using home name and password given

    * admins can post jobs on their specific home page 
    * jobs will include a value 
    * kid will be able to see jobs in their specific home
    *kid completes job then awaits admins approval
    *once approved by admin the amount/value of job is transferred into that kids wallet/account
    -place where admins and kids can see all jobs that were completed and approved
    -section where kid can spend the coins through a menu type list with costs

    ####problems
    -validate age to be an admin
    -only users not in home can see list can see list of homes
    ->user who is not admin cant see personal home name on home page
    -validate jobs
    -other admins who are NOT creators cannot post a job
    -not all admins can approve completed jobs only creators


query = "select first_name, last_name, sum(value) as kid_coins from jobs join users on completed_by = users.id WHERE completed = true AND approved = true GROUP BY completed_by"


query = "SELECT * FROM family join users on user_id = users.id where home_id = 14"
     