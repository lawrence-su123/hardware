from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage
from django.conf import settings  # Import settings

import stripe

# Set your secret key from settings
stripe.api_key = settings.STRIPE_API_KEY

# Endpoint secret from settings
endpoint_secret = settings.STRIPE_ENDPOINT_SECRET

def welcome_view(request):
    return render(request, 'welcome.html')

@csrf_exempt
def my_webhook_view(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        # Retrieve the session. If you require line items in the response, you may include them by expanding line_items.
        session = stripe.checkout.Session.retrieve(
            event['data']['object']['id'],
            expand=['line_items'],
        )

        customer_email = session.customer_details.email
        
        # Website link and passcode
        website_link = "https://docs.hardwareinterviews.fyi"
        passcode = "CompletelyOutoftheWorld2023!"

        # Send email with website link and passcode
        subject = 'Hardware FYI Pro Access'
        message = f"Thank you for your purchase!\n\nURL: {website_link}\nPW: {passcode}"
        from_email = settings.EMAIL_HOST_USER  # Use the email from settings
        recipient_list = [customer_email]

        email = EmailMessage(
            subject, message, from_email, recipient_list
        )

        try:
            email.send()
        except Exception as e:
            # Handle email sending error
            print("Email sending error:", e)

    return HttpResponse(status=200)
