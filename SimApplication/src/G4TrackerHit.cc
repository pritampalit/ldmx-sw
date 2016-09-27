#include "SimApplication/G4TrackerHit.h"

// Geant4
#include "G4VVisManager.hh"
#include "G4VisAttributes.hh"
#include "G4Point3D.hh"
#include "G4Circle.hh"

G4Allocator<G4TrackerHit> G4TrackerHitAllocator;

G4TrackerHit::G4TrackerHit()
    : simTrackerHit(new SimTrackerHit()), trackID(-1) {
}

G4TrackerHit::G4TrackerHit(SimTrackerHit* theSimTrackerHit)
    : simTrackerHit(theSimTrackerHit), trackID(-1) {
}

G4TrackerHit::~G4TrackerHit() {
}

SimTrackerHit* G4TrackerHit::getSimTrackerHit() {
    return simTrackerHit;
}

void G4TrackerHit::Draw() {

    G4VVisManager* visManager = G4VVisManager::GetConcreteInstance();

    if(visManager) {

        G4Point3D p3D = G4Point3D(getPosition());
        G4Circle chit(p3D);
        chit.SetScreenDiameter(3.0);
        chit.SetFillStyle(G4Circle::filled);

        G4Colour col(1.0, 0.0, 1.0);

        chit.SetVisAttributes(G4VisAttributes(col));
        visManager->Draw(chit);
    }
}

void G4TrackerHit::Print() {
    simTrackerHit->Print();
}

G4ThreeVector G4TrackerHit::getPosition() {

    G4ThreeVector startPos = G4ThreeVector(
            simTrackerHit->getStartPosition()[0],
            simTrackerHit->getStartPosition()[1],
            simTrackerHit->getStartPosition()[2]);

    G4ThreeVector endPos = G4ThreeVector(
            simTrackerHit->getEndPosition()[0],
            simTrackerHit->getEndPosition()[1],
            simTrackerHit->getEndPosition()[2]);

    return (0.5 * (startPos + endPos));
}

G4int G4TrackerHit::getTrackID() {
    return trackID;
}

void G4TrackerHit::setStartPosition(const G4ThreeVector& startPosition) {
    simTrackerHit->setStartPosition(startPosition[0], startPosition[1], startPosition[2]);
}

void G4TrackerHit::setEndPosition(const G4ThreeVector& endPosition) {
    simTrackerHit->setEndPosition(endPosition[0], endPosition[1], endPosition[2]);
}

void G4TrackerHit::setMomentum(const G4ThreeVector& p) {
    simTrackerHit->setMomentum(p[0], p[1], p[2]);
}

void G4TrackerHit::setTrackID(G4int aTrackID) {
    this->trackID = aTrackID;
}