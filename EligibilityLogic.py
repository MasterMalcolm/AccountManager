def evaluate_transfer_eligibility(profile):
    """
    Evaluates statutory compliance based on 2025-2026 NCAA and NAIA rules.
    """
    blockers = []
    caveats = []
    
    # Baseline universal checks
    if not profile.in_good_standing:
        blockers.append("Student is under disciplinary probation or not in good academic standing.")
        
    if profile.competed_same_championship_season:
        blockers.append("Cannot compete for two institutions in the same sport during the same championship segment.")

    dest = profile.target_division

    # Division I Rules (Proposal 2024-5 Framework)
    if dest == 'DI':
        if not profile.academically_eligible_prior:
            blockers.append("NCAA DI mandates academic eligibility upon departure from the prior 4-year school.")
        if not profile.entered_portal_during_window:
            blockers.append("Missed the designated sport-specific NCAA Transfer Portal window.")
        caveats.append("Must meet destination institution Progress-Toward-Degree (PTD) requirements (40/60/80%).")
        citation = "NCAA DI Proposal 2024-5 (Rescinded one-time transfer limit; immediate eligibility standard)."

    # Division II Rules (EM-2025-1)
    elif dest == 'DII':
        if not profile.academically_eligible_prior:
            blockers.append("Requires athletic & academic eligibility at origin, or serve 1 regular term in residence.")
        if profile.last_term_credit_hours < 9:
            blockers.append("Must pass a minimum of 9 semester / 8 quarter transferable hours in the preceding term.")
        citation = "NCAA DII Bylaw 14.5.5 / EM-2025-1."

    # Division III Rules
    elif dest == 'DIII':
        if not profile.academically_eligible_prior:
            blockers.append("Must be academically eligible had you remained, or serve a one-term academic sit-out.")
        caveats.append("Recruiting requires official completion of the NCAA Division III Self-Release form.")
        citation = "NCAA DIII Bylaw 14.5.5 (Immediate eligibility upon standard academic release)."

    # NAIA Rules
    elif dest == 'NAIA':
        if profile.last_term_credit_hours < 12:
            blockers.append("Must satisfy the NAIA 24/36-hour rule for multi-term athletes.")
        caveats.append("National 16-week residency abolished, but individual conferences may enforce intra-league rules.")
        citation = "NAIA Article V, Section G (General residency rescinded; eligibility statement mandatory)."

    else:
        caveats.append("Check individual association rules (USCAA/NCCAA) for residency requirements.")
        citation = "Independent Collegiate Athletic Association Bylaws."

    return {
        'is_eligible': len(blockers) == 0,
        'blockers': blockers,
        'caveats': caveats,
        'citation': citation
    }