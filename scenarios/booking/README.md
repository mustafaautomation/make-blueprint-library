# Booking

Portfolio demos by Mustafa ([mustafaautomation](https://github.com/mustafaautomation)). Not client work.

Confirm, remind, and brief people around a booking.

| Scenario | Difficulty | Description |
| --- | --- | --- |
| [Calendly or Cal.com booking confirmation](appointment-booking-confirm/) | beginner | On a booking webhook, log the invitee, email a confirmation, and text them. Cancellations take the other route. |
| [Day-before appointment reminder from the sheet](appointment-day-before-reminder/) | beginner | Text each sheet row whose remind flag is YES. Pair it with the booking confirmation scenario. |
| [No-show webhook texts a rebook line](no-show-text-back/) | beginner | When a booking payload says no-show, text a one-line rebook note. |
| [Pre-meeting intake brief for the host](intake-brief-for-host/) | intermediate | Turn an intake form into a five-line brief and post it when the brief is actually about the meeting. |
| [Reschedule webhook logged and acknowledged](reschedule-webhook-log/) | beginner | Log a reschedule payload and tell Slack the old and new times. |
| [Route a booking ping by host name](round-robin-host-ping/) | beginner | Ping Slack with the host name, and only page when the host field is filled. |
