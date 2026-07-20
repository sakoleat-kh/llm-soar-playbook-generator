"""
Baseline classifiers for evaluation.

These provide simple reference points againts which the LMM-based
classifier can be compared
"""

from __future__ import annotations

import random

TECHNIQUES = {
    "T1566.001": "Phishing",
    "T10559": "Command and Scripting Interpreter",
    "T1078": "Valid Accounts",
    "T1021": "Remote Services",
}

KEYWORD_MAP = {
    # phishing
    "phishing": "T1566.001",
    "email": "T1566.001",
    "attachment": "T1566.001",    
    "macro": "T1566.001",

    # Command execution
    "script": "T1059",
    "powershell": "T1059",
    "cmd": "T1059",
    "bash": "T1078",

    # alid accounts
    "login": "T1078",
    "credential": "T1078",
    "password": "T1078",
    "vpn": "T1078",

    #Remote services
    "rdp": "T1021",
    "remote desktop": "T1021",
    "ssh": "T1021",
    "winrm": "T1021",
}

def keyword_classifier(text: str) -> str:
    """
    Rule-based classifier using keyword matching.

    Returns:
        ATT&CK technique ID.
    """

    text = text.lower()

    for keyword, technique in KEYWORD_MAP.items():
        if keyword in text:
            return technique
        
    # Default majority / fallback class
    return "T1078"

def random_classifier(text: str) -> str:
    """
    Random baseline classifier.
    """

    return random.choice(list(TECHNIQUES.keys()))
