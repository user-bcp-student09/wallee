"""Destinos de los archivos NestJS y React que emite el AI Engineer."""

import unittest

from crew.code_paths import feature_slug, guess_filename, resolve_destination


class CodePathTests(unittest.TestCase):
    def test_explicit_project_paths_are_kept(self):
        self.assertEqual(
            resolve_destination("backend-nestjs/src/auth/auth.service.ts", "", "x"),
            "backend-nestjs/src/auth/auth.service.ts",
        )
        self.assertEqual(
            resolve_destination("frontend-react/package.json", "", "x"),
            "frontend-react/package.json",
        )

    def test_app_repository_roots_are_kept(self):
        for target in ("backend/test/onboarding.e2e-spec.ts", "frontend/src/onboarding/Onboarding.test.tsx",
                       "backend/src/wallet/wallet.service.ts"):
            self.assertEqual(resolve_destination(target, "", "x"), target)
        self.assertEqual(resolve_destination("output/backend/test/a.e2e-spec.ts", "", "x"), "backend/test/a.e2e-spec.ts")

    def test_app_repository_roots_still_reject_unsafe_or_bare_roots(self):
        for target in ("backend", "frontend/../../x.ts", "backend/../x.ts"):
            self.assertIsNone(resolve_destination(target, "", "x"), target)

    def test_unsafe_paths_are_rejected(self):
        for target in ("../x.ts", "/etc/x.ts", "C:/x.ts", "frontend-react/../../x.ts"):
            self.assertIsNone(resolve_destination(target, "", "x"), target)

    def test_bare_names_are_classified_by_content(self):
        nest = "import { Injectable } from '@nestjs/common';"
        react = "import { useState } from 'react';"
        self.assertEqual(
            resolve_destination("create-transfer.dto.ts", nest, "wallet"),
            "backend-nestjs/src/wallet/dto/create-transfer.dto.ts",
        )
        self.assertEqual(
            resolve_destination("transfer.service.ts", react, "wallet"),
            "frontend-react/src/wallet/transfer.service.ts",
        )
        self.assertEqual(
            resolve_destination("src/auth/Login.tsx", react, "wallet"),
            "frontend-react/src/auth/Login.tsx",
        )
        self.assertIsNone(resolve_destination("package.json", "{}", "wallet"))

    def test_names_are_guessed_from_declarations(self):
        self.assertEqual(
            guess_filename("import { Controller } from '@nestjs/common';\nexport class UserTransferController {}"),
            "user-transfer.controller.ts",
        )
        self.assertEqual(
            guess_filename("import React from 'react';\nexport default function Login() { return <div />; }"),
            "Login.tsx",
        )

    def test_feature_slug(self):
        self.assertEqual(feature_slug("Transferir fondos ñandú"), "transferir-fondos-nandu")
        self.assertEqual(feature_slug(""), "feature")


if __name__ == "__main__":
    unittest.main()
