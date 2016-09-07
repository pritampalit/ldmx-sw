#include "Event/SimCalorimeterHit.h"

ClassImp(SimCalorimeterHit)

SimCalorimeterHit::SimCalorimeterHit() :
    _id(0),
    _edep(0.) {

    _position[0] = 0.;
    _position[1] = 0.;
    _position[2] = 0.;
}

SimCalorimeterHit::~SimCalorimeterHit() {
}

long SimCalorimeterHit::id() {
    return _id;
}

double SimCalorimeterHit::edep() {
    return _edep;
}

double* SimCalorimeterHit::position() {
    return _position;
}

void SimCalorimeterHit::setId(long id) {
    _id = id;
}

void SimCalorimeterHit::setEdep(double edep) {
    _edep = edep;
}

void SimCalorimeterHit::setPosition(double x, double y, double z) {
    _position[0] = x;
    _position[1] = y;
    _position[2] = z;
}
