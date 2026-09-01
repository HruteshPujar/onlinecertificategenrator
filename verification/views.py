from django.shortcuts import render, get_object_or_404

from .models import CertificateVerification


def verify_certificate(request, verification_code):

    verification = get_object_or_404(
        CertificateVerification,
        verification_code=verification_code
    )

    participant = verification.participant

    return render(
        request,
        "verification/verify.html",
        {
            "verification": verification,
            "participant": participant,
        },
    )