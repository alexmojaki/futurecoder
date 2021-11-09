import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {faUser} from "@fortawesome/free-solid-svg-icons";
import StyledFirebaseAuth from "react-firebaseui/StyledFirebaseAuth";
import firebase from "firebase";
import {updateDatabase} from "../book/store";
import Popup from "reactjs-popup";

const HeaderLoginInfo = ({ email }) => {
  return email ?
    <><FontAwesomeIcon icon={faUser}/> {email}</> :
    <Popup
      trigger={
      <button className="btn btn-primary">
        <FontAwesomeIcon icon={faUser}/> Login / Sign up
      </button>
    }
    modal
    closeOnDocumentClick
  >
    {close =>
      <StyledFirebaseAuth
        uiConfig={{
          signInOptions: [
            {
              provider: firebase.auth.EmailAuthProvider.PROVIDER_ID,
              requireDisplayName: false,
            },
            // TODO not working because of cross origin isolation
            // firebase.auth.GoogleAuthProvider.PROVIDER_ID,
            // firebase.auth.FacebookAuthProvider.PROVIDER_ID,
            // firebase.auth.GithubAuthProvider.PROVIDER_ID,
          ],
          autoUpgradeAnonymousUsers: true,
          callbacks: {
            // Avoid redirects after sign-in.
            signInSuccessWithAuthResult: () => {
              close();
              return false;
            },

            // Ignore merge conflicts when upgrading anonymous users and continue signing in
            // The store will merge the user data
            signInFailure: async (error) => {
              if (error.code === 'firebaseui/anonymous-upgrade-merge-conflict') {
                // Note the upgrade in the old anonymous account
                await updateDatabase({upgradedFromAnonymous: true});

                await firebase.auth().signInWithCredential(error.credential);
                close();
              }
            }
          }
        }}
        firebaseAuth={firebase.auth()}
      />
    }
  </Popup>
}

export default HeaderLoginInfo;
