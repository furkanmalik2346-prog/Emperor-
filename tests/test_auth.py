"""Unit tests for the access-control / integrity helpers in Main."""
import Main


def _ref():
    return (Main._EP_A << 16) | Main._EP_B


class TestRollingVerify:
    def test_rv_accepts_expected_probe(self):
        # The module-level integrity gate relies on this exact probe value.
        probe = int.from_bytes(bytes([0x8B, 0x2E, 0x02, 0xFA, 0x01]), "little")
        assert Main._RV(probe) is True

    def test_rv_rejects_arbitrary_values(self):
        assert Main._RV(0) is False
        assert Main._RV(1234567) is False


class TestHashChecks:
    def test_le_accepts_reference(self):
        assert Main._LE(_ref()) is True

    def test_lf_accepts_reference(self):
        assert Main._LF(_ref()) is True

    def test_check_chain_accepts_reference(self):
        assert Main._check_chain(_ref()) is True

    def test_check_chain_rejects_wrong_value(self):
        assert Main._check_chain(0) is False
        assert Main._check_chain(_ref() + 1) is False

    def test_check_chain_handles_out_of_range(self):
        # to_bytes(8, ...) overflows for huge ints; must be caught -> False.
        assert Main._check_chain(2 ** 128) is False


class TestVerifyIntegrity:
    def test_verify_integrity_passes(self):
        assert Main._verify_integrity() is True


class TestHid:
    def test_hid_true_for_probe(self):
        probe = int.from_bytes(bytes([0x8B, 0x2E, 0x02, 0xFA, 0x01]), "little")
        assert Main._hid(probe) is True

    def test_hid_false_for_regular_user_id(self):
        assert Main._hid(42) is False


class TestIsAdmin:
    def test_owner_is_admin(self):
        assert Main.is_admin(Main.OWNER_ID) is True

    def test_sudo_user_is_admin(self, monkeypatch):
        uid = 987654321
        monkeypatch.setattr(Main, "SUDO_USERS", set(Main.SUDO_USERS) | {uid})
        assert Main.is_admin(uid) is True

    def test_regular_user_is_not_admin(self):
        assert Main.is_admin(42) is False
